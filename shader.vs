#version 150
/* #############################################################################

 OpenGL Instancing Example
 Authors:
  - Richard Petri <dasricht at gmail.com>

 This is free and unencumbered software released into the public domain.

 Anyone is free to copy, modify, publish, use, compile, sell, or
 distribute this software, either in source code form or as a compiled
 binary, for any purpose, commercial or non-commercial, and by any
 means.

 In jurisdictions that recognize copyright laws, the author or authors
 of this software dedicate any and all copyright interest in the
 software to the public domain. We make this dedication for the benefit
 of the public at large and to the detriment of our heirs and
 successors. We intend this dedication to be an overt act of
 relinquishment in perpetuity of all present and future rights to this
 software under copyright law.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
 OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 OTHER DEALINGS IN THE SOFTWARE.

 For more information, please refer to <http://unlicense.org/>

############################################################################# */

// Model-view Projection
uniform mat4 mvp;
// Object Projection
uniform mat4 objp;
// Offset possition per instance
uniform vec4 objoffset[125];

in vec4 vs_position;
in vec4 vs_normal;
out vec4 fs_color;

void main() {
  fs_color = vec4((vs_normal.xyz/2.0)+0.5, 1.0);
  gl_Position = mvp * ((objp * vs_position) + objoffset[gl_InstanceID]);
}