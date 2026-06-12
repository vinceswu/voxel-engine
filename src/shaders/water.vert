#version 330 core

layout (location = 0) in vec2 in_tex_coord;
layout (location = 1) in vec3 in_position;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform int water_area;
uniform float water_line;
uniform vec2 u_cam_pos;

out vec2 uv;

void main() {
    vec3 pos = in_position;

    pos.xz = u_cam_pos + (pos.xz - 0.5) * water_area;

    pos.y += water_line;
    uv = pos.xz;
    gl_Position = m_proj * m_view * vec4(pos, 1.0);
}
