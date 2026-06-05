import numpy as np

_voxel_cache = {}
_STRETCH2 = -0.211324865405187
_SQUISH2 = 0.366025403784439


def _extrap2(perm, grad2, xsb, ysb, dx, dy):
    idx = perm[(perm[xsb & 255] + ysb) & 255] & 14
    return grad2[idx] * dx + grad2[idx + 1] * dy


def gen_cloud_data(perm_list, grad2_list, width, depth, scale=0.13, threshold=0.2):
    perm = np.array(perm_list, dtype=np.int64)
    grad2 = np.array(grad2_list, dtype=np.float64)

    xi = np.tile(np.arange(width, dtype=np.float64), depth)
    zi = np.repeat(np.arange(depth, dtype=np.float64), width)
    x = xi * scale
    y = zi * scale

    so = (x + y) * _STRETCH2
    xs, ys = x + so, y + so
    xsb = np.floor(xs).astype(np.int64)
    ysb = np.floor(ys).astype(np.int64)
    sq = (xsb + ysb).astype(np.float64) * _SQUISH2
    dx0 = x - (xsb.astype(np.float64) + sq)
    dy0 = y - (ysb.astype(np.float64) + sq)
    xins = xs - xsb.astype(np.float64)
    yins = ys - ysb.astype(np.float64)
    in_sum = xins + yins

    val = np.zeros(len(x), dtype=np.float64)

    def add_contrib(xb, yb, ddx, ddy):
        a = 2.0 - ddx * ddx - ddy * ddy
        m = a > 0
        if m.any():
            a2 = np.where(m, a * a, 0.0)
            val[m] += (a2 * a2 * _extrap2(perm, grad2, xb, yb, ddx, ddy))[m]

    add_contrib(xsb + 1, ysb, dx0 - 1.0 - _SQUISH2, dy0 - _SQUISH2)
    add_contrib(xsb, ysb + 1, dx0 - _SQUISH2, dy0 - 1.0 - _SQUISH2)

    xsv_e = np.empty_like(xsb)
    ysv_e = np.empty_like(ysb)
    dx_e = np.empty_like(dx0)
    dy_e = np.empty_like(dy0)
    xsb2 = xsb.copy()
    ysb2 = ysb.copy()
    dx02 = dx0.copy()
    dy02 = dy0.copy()

    lo = in_sum <= 1.0
    hi = ~lo
    z_lo = 1.0 - in_sum
    z_hi = 2.0 - in_sum

    branch = lo & ((z_lo > xins) | (z_lo > yins))
    xa = branch & (xins > yins)
    ya = branch & ~(xins > yins)
    xsv_e = np.where(xa, xsb + 1, np.where(ya, xsb - 1, xsv_e))
    ysv_e = np.where(xa, ysb - 1, np.where(ya, ysb + 1, ysv_e))
    dx_e = np.where(xa, dx0 - 1.0, np.where(ya, dx0 + 1.0, dx_e))
    dy_e = np.where(xa, dy0 + 1.0, np.where(ya, dy0 - 1.0, dy_e))

    nb = lo & ~((z_lo > xins) | (z_lo > yins))
    xsv_e = np.where(nb, xsb + 1, xsv_e)
    ysv_e = np.where(nb, ysb + 1, ysv_e)
    dx_e = np.where(nb, dx0 - 1.0 - 2.0 * _SQUISH2, dx_e)
    dy_e = np.where(nb, dy0 - 1.0 - 2.0 * _SQUISH2, dy_e)

    branch_hi = hi & ((z_hi < xins) | (z_hi < yins))
    xc = branch_hi & (xins > yins)
    yc = branch_hi & ~(xins > yins)
    xsv_e = np.where(xc, xsb + 2, np.where(yc, xsb, xsv_e))
    ysv_e = np.where(xc, ysb, np.where(yc, ysb + 2, ysv_e))
    dx_e = np.where(
        xc, dx0 - 2.0 - 2.0 * _SQUISH2, np.where(yc, dx0 - 2.0 * _SQUISH2, dx_e)
    )
    dy_e = np.where(
        xc, dy0 - 2.0 * _SQUISH2, np.where(yc, dy0 - 2.0 - 2.0 * _SQUISH2, dy_e)
    )

    nd = hi & ~((z_hi < xins) | (z_hi < yins))
    xsv_e = np.where(nd, xsb, xsv_e)
    ysv_e = np.where(nd, ysb, ysv_e)
    dx_e = np.where(nd, dx0, dx_e)
    dy_e = np.where(nd, dy0, dy_e)

    xsb2 += hi
    ysb2 += hi
    dx02 = np.where(hi, dx02 - 1.0 - 2.0 * _SQUISH2, dx02)
    dy02 = np.where(hi, dy02 - 1.0 - 2.0 * _SQUISH2, dy02)

    add_contrib(xsb2, ysb2, dx02, dy02)
    add_contrib(xsv_e, ysv_e, dx_e, dy_e)

    return (val >= threshold).astype(np.uint8)


def build_cloud_mesh(cloud_data_np, width, depth, cloud_height):
    grid = cloud_data_np.reshape(depth, width)
    zi, xi = np.where(grid)
    n = len(xi)
    if n == 0:
        return np.array([], dtype=np.uint16)
    y = int(cloud_height)
    x = xi.astype(np.uint16)
    z = zi.astype(np.uint16)
    x1 = (xi + 1).astype(np.uint16)
    z1 = (zi + 1).astype(np.uint16)
    yy = np.full(n, y, dtype=np.uint16)
    quads = np.stack(
        [
            np.column_stack([x, yy, z]),
            np.column_stack([x1, yy, z1]),
            np.column_stack([x1, yy, z]),
            np.column_stack([x, yy, z]),
            np.column_stack([x, yy, z1]),
            np.column_stack([x1, yy, z1]),
        ],
        axis=1,
    )
    return quads.reshape(-1)


def render_chunk(vao, program, m_model):
    program["m_model"].write(m_model)
    vao.render()


def create_vao(ctx, program, vbo, vbo_format, attr):
    return ctx.vertex_array(program, [(vbo, vbo_format, attr)], skip_errors=True)


def create_vao2(ctx, program, vbo, vbo_format, attr1, attr2):
    return ctx.vertex_array(
        program, [(vbo, vbo_format, attr1, attr2)], skip_errors=True
    )


def store_voxels(px, py, pz, voxels):
    _voxel_cache[(int(px), int(py), int(pz))] = voxels


def fetch_voxels(px, py, pz):
    return _voxel_cache.get((int(px), int(py), int(pz)))


_face_verts = np.array(
    [
        [[0, 1, 0], [0, 1, 1], [1, 1, 1], [0, 1, 0], [1, 1, 1], [1, 1, 0]],
        [[0, 0, 0], [1, 0, 1], [0, 0, 1], [0, 0, 0], [1, 0, 0], [1, 0, 1]],
        [[1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 0, 0], [1, 1, 1], [1, 0, 1]],
        [[0, 0, 0], [0, 1, 1], [0, 1, 0], [0, 0, 0], [0, 0, 1], [0, 1, 1]],
        [[0, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 0], [1, 1, 0], [1, 0, 0]],
        [[0, 0, 1], [1, 1, 1], [0, 1, 1], [0, 0, 1], [1, 0, 1], [1, 1, 1]],
    ],
    dtype="int32",
)

_face_normals = np.array(
    [
        [0, 1, 0],
        [0, -1, 0],
        [1, 0, 0],
        [-1, 0, 0],
        [0, 0, -1],
        [0, 0, 1],
    ],
    dtype="int32",
)


def _compute_ao_offsets():
    result = np.zeros((6, 4, 3, 3), dtype="int32")
    for face_id in range(6):
        nx, ny, nz = (
            int(_face_normals[face_id, 0]),
            int(_face_normals[face_id, 1]),
            int(_face_normals[face_id, 2]),
        )
        if face_id in (0, 1):
            dirs = [
                [(-1, 0, 0), (0, 0, -1), (-1, 0, -1)],
                [(-1, 0, 0), (0, 0, 1), (-1, 0, 1)],
                [(1, 0, 0), (0, 0, 1), (1, 0, 1)],
                [(1, 0, 0), (0, 0, -1), (1, 0, -1)],
            ]
        elif face_id in (2, 3):
            dirs = [
                [(0, -1, 0), (0, 0, -1), (0, -1, -1)],
                [(0, 1, 0), (0, 0, -1), (0, 1, -1)],
                [(0, 1, 0), (0, 0, 1), (0, 1, 1)],
                [(0, -1, 0), (0, 0, 1), (0, -1, 1)],
            ]
        else:
            dirs = [
                [(-1, 0, 0), (0, -1, 0), (-1, -1, 0)],
                [(-1, 0, 0), (0, 1, 0), (-1, 1, 0)],
                [(1, 0, 0), (0, 1, 0), (1, 1, 0)],
                [(1, 0, 0), (0, -1, 0), (1, -1, 0)],
            ]
        for ci, corner in enumerate(dirs):
            for si, (dx, dy, dz) in enumerate(corner):
                result[face_id, ci, si] = [nx + dx, ny + dy, nz + dz]
    return result


_ao_offsets = _compute_ao_offsets()


def _compute_vert_corner_indices():
    result = np.zeros((6, 6), dtype="int32")
    for face_id in range(6):
        unique = []
        for vi in range(6):
            v = tuple(_face_verts[face_id, vi].tolist())
            if v not in unique:
                unique.append(v)
        for vi in range(6):
            v = tuple(_face_verts[face_id, vi].tolist())
            result[face_id, vi] = unique.index(v)
    return result


_vert_corner_idx = _compute_vert_corner_indices()


def _is_solid_arr(voxels, x, y, z, cs):
    valid = (x >= 0) & (x < cs) & (y >= 0) & (y < cs) & (z >= 0) & (z < cs)
    result = np.zeros_like(valid)
    w = np.where(valid)[0]
    if len(w) > 0:
        flat = x[w] + cs * z[w] + cs * cs * y[w]
        result[w] = voxels[flat] != 0
    return result


def build_chunk_mesh(chunk_voxels, format_size, chunk_pos, world_voxels):
    cs = 48
    ca = cs * cs

    if chunk_voxels is None:
        return np.array([], dtype="uint32")

    solid = chunk_voxels.astype(bool)
    solid_idx = np.where(solid)[0]
    n = len(solid_idx)
    if n == 0:
        return np.array([], dtype="uint32")

    xs = (solid_idx % cs).astype("int32")
    zs = ((solid_idx // cs) % cs).astype("int32")
    ys = (solid_idx // ca).astype("int32")
    vids = chunk_voxels[solid_idx].astype("int32")

    parts = []

    for face_id in range(6):
        nx, ny, nz = (
            int(_face_normals[face_id, 0]),
            int(_face_normals[face_id, 1]),
            int(_face_normals[face_id, 2]),
        )

        adj_x = xs + nx
        adj_y = ys + ny
        adj_z = zs + nz

        in_bounds = (
            (adj_x >= 0)
            & (adj_x < cs)
            & (adj_y >= 0)
            & (adj_y < cs)
            & (adj_z >= 0)
            & (adj_z < cs)
        )
        neighbor_solid = np.zeros(n, dtype=bool)
        ib = np.where(in_bounds)[0]
        if len(ib) > 0:
            flat_nb = adj_x[ib] + cs * adj_z[ib] + ca * adj_y[ib]
            neighbor_solid[ib] = solid[flat_nb]

        oob = ~in_bounds
        if np.any(oob):
            ncx = int(chunk_pos[0]) + nx
            ncy = int(chunk_pos[1]) + ny
            ncz = int(chunk_pos[2]) + nz
            neighbor_chunk = _voxel_cache.get((ncx, ncy, ncz))
            if neighbor_chunk is not None:
                oob_idx = np.where(oob)[0]
                lx = adj_x[oob_idx] % cs
                ly = adj_y[oob_idx] % cs
                lz = adj_z[oob_idx] % cs
                flat_nb = lx + cs * lz + ca * ly
                neighbor_solid[oob_idx] = neighbor_chunk[flat_nb] != 0

        exposed = ~neighbor_solid
        sel = np.where(exposed)[0]
        nsel = len(sel)
        if nsel == 0:
            continue

        sel_x = xs[sel]
        sel_y = ys[sel]
        sel_z = zs[sel]
        sel_vid = vids[sel]

        ao_corners = np.full((nsel, 4), 3, dtype="int32")

        for ci in range(4):
            for si in range(3):
                dx, dy, dz = (
                    int(_ao_offsets[face_id, ci, si, 0]),
                    int(_ao_offsets[face_id, ci, si, 1]),
                    int(_ao_offsets[face_id, ci, si, 2]),
                )
                sample_solid = _is_solid_arr(
                    chunk_voxels, sel_x + dx, sel_y + dy, sel_z + dz, cs
                )
                if si < 2:
                    ao_corners[:, ci] -= sample_solid.astype("int32")
                else:
                    dx1, dy1, dz1 = (
                        int(_ao_offsets[face_id, ci, 0, 0]),
                        int(_ao_offsets[face_id, ci, 0, 1]),
                        int(_ao_offsets[face_id, ci, 0, 2]),
                    )
                    dx2, dy2, dz2 = (
                        int(_ao_offsets[face_id, ci, 1, 0]),
                        int(_ao_offsets[face_id, ci, 1, 1]),
                        int(_ao_offsets[face_id, ci, 1, 2]),
                    )
                    s1 = _is_solid_arr(
                        chunk_voxels, sel_x + dx1, sel_y + dy1, sel_z + dz1, cs
                    )
                    s2 = _is_solid_arr(
                        chunk_voxels, sel_x + dx2, sel_y + dy2, sel_z + dz2, cs
                    )
                    both_solid = s1 & s2
                    ao_corners[:, ci] -= (sample_solid & ~both_solid).astype("int32")

        ao_corners = np.clip(ao_corners, 0, 3)

        c0 = _vert_corner_idx[face_id, 0]
        c1 = _vert_corner_idx[face_id, 1]
        c2 = _vert_corner_idx[face_id, 2]
        c3 = (
            _vert_corner_idx[face_id, 4]
            if (face_id & 1)
            else _vert_corner_idx[face_id, 5]
        )
        flip = (
            (ao_corners[:, c1] + ao_corners[:, c3])
            > (ao_corners[:, c0] + ao_corners[:, c2])
        ).astype("uint32")

        fv = _face_verts[face_id]
        vci = _vert_corner_idx[face_id]

        for vi in range(6):
            vx, vy, vz = int(fv[vi, 0]), int(fv[vi, 1]), int(fv[vi, 2])
            ci = vci[vi]
            vert_x = (sel_x + vx).astype("uint32")
            vert_y = (sel_y + vy).astype("uint32")
            vert_z = (sel_z + vz).astype("uint32")
            ao = ao_corners[:, ci].astype("uint32")
            fid = np.full(nsel, face_id, dtype="uint32")

            packed = (
                (vert_x << 26)
                | (vert_y << 20)
                | (vert_z << 14)
                | (sel_vid.astype("uint32") << 6)
                | (fid << 3)
                | (ao << 1)
                | flip
            )
            parts.append(packed)

    if not parts:
        return np.array([], dtype="uint32")

    result_parts = []
    i = 0
    while i < len(parts):
        face_arrays = parts[i : i + 6]
        stacked = np.column_stack(face_arrays)
        result_parts.append(stacked.ravel())
        i += 6

    return np.concatenate(result_parts)
