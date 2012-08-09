#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#  OpenGL 3.2 Core Profile Example
#  Authors:
#   - Richard Petri <dasricht at gmail.com>
#
#  This is free and unencumbered software released into the public domain.
#  
#  Anyone is free to copy, modify, publish, use, compile, sell, or
#  distribute this software, either in source code form or as a compiled
#  binary, for any purpose, commercial or non-commercial, and by any
#  means.
#  
#  In jurisdictions that recognize copyright laws, the author or authors
#  of this software dedicate any and all copyright interest in the
#  software to the public domain. We make this dedication for the benefit
#  of the public at large and to the detriment of our heirs and
#  successors. We intend this dedication to be an overt act of
#  relinquishment in perpetuity of all present and future rights to this
#  software under copyright law.
#  
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.
#   
#  For more information, please refer to <http://unlicense.org/>
#
##############################################################################

import numpy as np
import pycgtools.hommat as hm
from pycgtools.glfw import *
from OpenGL.arrays.vbo import VBO
from OpenGL.GL.ARB.vertex_array_object import *
import pycgtools.demoplate as df
import pycgtools.shaderutil as su

class instancingdemo(df.demoplate):
    
    def init(self):
        self.cubedata = np.array([-1,-1, 1, 1, 0, 0, 0, 0, #1
                                  1,-1, 1, 1, 1, 0, 0, 0, #2
                                  1, 1, 1, 1, 1, 1, 0, 0, #3
                                  1,-1,-1, 1, 1, 0, 1, 0, #4
                                  1, 1,-1, 1, 1, 1, 1, 0, #5
                                 -1, 1,-1, 1, 0, 1, 1, 0, #6
                                  1, 1, 1, 1, 1, 1, 0, 0, #7
                                 -1, 1, 1, 1, 0, 1, 0, 0, #8
                                 -1,-1, 1, 1, 0, 0, 0, 0, #9
                                 -1, 1,-1, 1, 0, 1, 1, 0, #10
                                 -1,-1,-1, 1, 0, 0, 1, 0, #11
                                  1,-1,-1, 1, 1, 0, 1, 0, #12
                                 -1,-1, 1, 1, 0, 0, 0, 0, #13
                                  1,-1, 1, 1, 1, 0, 0, 0, #14
                                  ], dtype = np.float32)
                            
        self.campos = np.array([2.5, 1.5, 2.5, 1], dtype = np.float32)
        self.center = np.array([0.0,0.0,0.0,1.0], dtype = np.float32)
        
        self.modelview_mat = hm.lookat(hm.identity(),
                                       self.campos,
                                       self.center)
        self.perspective_mat = None
        self.mvp = None
        # OpenGL Stuff
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glClearColor(1, 1, 1, 0)
        glPointSize(5)
        # Shader Stuff.
        with open('shader.fs') as fs, open('shader.vs') as vs:            
            self.shader = su.Shader(list(vs), list(fs))
        
        self.shader.bindfragdata(0, 'fragcolor')
        self.mvploc = self.shader.uniformlocation('mvp')
        positionloc = self.shader.attributelocation('vs_position')
        colorloc = self.shader.attributelocation('vs_color')
        # Object data stuff.
        self.vertobj = glGenVertexArrays(1)
        glBindVertexArray(self.vertobj)
        # Setup the VBO (using the fancy VBO Object from pyopengl, doing it "manually" would also be a possibility)
        self.vertbuf = VBO(self.cubedata, GL_STATIC_DRAW)
        self.vertbuf.bind()
        glEnableVertexAttribArray(positionloc)
        glEnableVertexAttribArray(colorloc)
        glVertexAttribPointer(positionloc, 4, GL_FLOAT, GL_TRUE, 8 * 4, self.vertbuf+0) # "+0" since we need to create an offset.
        glVertexAttribPointer(colorloc, 4, GL_FLOAT, GL_TRUE, 8 * 4, self.vertbuf+16) # 4 * 4 Bytes per float.
        self.vertbuf.unbind() # We can unbind the VBO, since it's linked to the VAO
        self.rotation = 0
                
    def resize(self, width, height):
        glViewport(0, 0, width, height)
        self.perspective_mat = hm.perspective(hm.identity(),
                                              70,
                                              float(width) / height,
                                              0.1,
                                              10.0)
        self.mvp = np.dot(self.perspective_mat, self.modelview_mat)
    
    def display(self, timediff):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.shader.use()
        glUniformMatrix4fv(self.mvploc, 1, GL_TRUE,
                           hm.rotation(self.mvp, self.rotation, [0,1,0]).tolist())
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 14)
        glDrawArrays(GL_POINTS, 0, 14)
        
        self.rotation += timediff / 5 * 360

if __name__ == '__main__':
    instancingdemo(windowhints = df.OSX_CORE_PROFILE_HINTS).run()
    