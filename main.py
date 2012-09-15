#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#  OpenGL Instancing Example
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
import pycgtools.wavefront as wf

class instancingdemo(df.demoplate):
    
    def init(self):
        print "OpenGL Information:"
        for prop in ["GL_VENDOR", "GL_RENDERER", "GL_VERSION", "GL_SHADING_LANGUAGE_VERSION"]:
            print "\t%s = %s" % (prop, glGetString(globals()[prop]))

        
        self.campos = np.array([2.5, 1.5, 1.5, 1], dtype = np.float32)
        self.center = np.array([0.0,0.0,0.0,1.0], dtype = np.float32)
        
        self.perspective_mat = None
        self.mvp = None
        # OpenGL Stuff
        glEnable(GL_DEPTH_TEST)
        #glEnable(GL_CULL_FACE)
        glClearColor(1, 1, 1, 0)
        glPointSize(5)
        # Shader Stuff.
        with open('shader.fs') as fs, open('shader.vs') as vs:            
            self.shader = su.Shader(list(vs), list(fs))
        
        self.shader.bindfragdata(0, 'fragcolor')
        self.mvploc = self.shader.uniformlocation('mvp')
        self.objploc = self.shader.uniformlocation('objp')
        self.objoffsetloc = self.shader.uniformlocation('objoffset')
        self.positionloc = self.shader.attributelocation('vs_position')
        self.normalloc = self.shader.attributelocation('vs_normal')
        
        self.loadsquirrel()
        self.buildobjoffsets()
        
    def buildobjoffsets(self):
        objoffset = np.zeros((5,5,5,4), dtype = np.float32)
        start = np.array([-1, -1, -1, 0], dtype = np.float32)
        steps = np.arange(0, 2.1, 0.5, dtype = np.float32)
        for x in range(5):
            for y in range(5):
                for z in range(5):
                    objoffset[x,y,z,] = start + np.array([steps[x], steps[y], steps[z], 0], dtype = np.float32)
        self.shader.use()
        glUniform4fv(self.objoffsetloc, 5 * 5 * 5, objoffset.flatten().tolist())
                
    def loadsquirrel(self):
        # When loading the data, pad the normals to 4 floats (16bytes) since GPUs hate unaligned memory.
        obj = wf.ObjFileParser("squirrel.obj", padnormals = 4)
        self.objscale = 1 / np.max(obj.scale / 2)
        self.objcenter = obj.minpos + (obj.scale / 2)
        
        self.obj_mat = hm.scale(hm.identity(),
                                [self.objscale * 0.2] * 3)
        self.obj_mat = hm.translation(self.obj_mat,
                                      -self.objcenter)

        # Generate a GL compatible indexed vertex buffer for the object
        self.vbdata, ibdata = obj.generateIndexedBuffer([0,1], np.uint16)
        vbdata = self.vbdata
        self.elementnum = np.shape(ibdata)[0]
        # VAO
        self.vertobj = glGenVertexArrays(1)
        glBindVertexArray(self.vertobj)
        # Setup the VBO for the vertex data.
        self.vertbuf = VBO(vbdata, GL_STATIC_DRAW, GL_ARRAY_BUFFER)
        self.vertbuf.bind()
        glVertexAttribPointer(self.positionloc, 4, GL_FLOAT, GL_TRUE, 8 * 4, ctypes.c_void_p(0))
        glVertexAttribPointer(self.normalloc, 4, GL_FLOAT, GL_TRUE, 8 * 4, ctypes.c_void_p(16))
        glEnableVertexAttribArray(self.positionloc)
        glEnableVertexAttribArray(self.normalloc)
        # Indexbuffer
        self.indexbuf = VBO(ibdata, GL_STATIC_DRAW, GL_ELEMENT_ARRAY_BUFFER)
        self.indexbuf.bind()
        
        glBindVertexArray(0)
        self.vertbuf.unbind()
        self.indexbuf.unbind()
        #Animation init...
        self.rotation = 0

                
    def resize(self, width, height):
        glViewport(0, 0, width, height)
        self.perspective_mat = hm.perspective(hm.identity(),
                                              60,
                                              float(width) / height,
                                              0.1,
                                              6.0)
        self.modelview_mat = hm.lookat(hm.identity(),
                                       self.campos,
                                       self.center)
        
        self.mvp = np.dot(self.perspective_mat, self.modelview_mat)
    
    def display(self, timediff):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.shader.use()
        glUniformMatrix4fv(self.objploc, 1, GL_TRUE,
                           np.dot(hm.rotation(hm.identity(), self.rotation, [0,1,0]), self.obj_mat).tolist())
        glUniformMatrix4fv(self.mvploc, 1, GL_TRUE,
                           hm.rotation(self.mvp, self.rotation / 4, [0.577350269189626] * 3).tolist())
        
        glBindVertexArray(self.vertobj)
        glDrawElementsInstanced(GL_TRIANGLES, self.elementnum, GL_UNSIGNED_SHORT, ctypes.c_void_p(0), 125)
        glBindVertexArray(0)
        
        self.rotation += timediff / 5 * 360

if __name__ == '__main__':
    instancingdemo(windowhints = df.OSX_CORE_PROFILE_HINTS).run()
    