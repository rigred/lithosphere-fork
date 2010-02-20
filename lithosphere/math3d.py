# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

import math

class Vector(object):
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __mul__(self, scalar):
        return Vector(
            x = self.x * scalar,
            y = self.y * scalar,
            z = self.z * scalar,
        )

    def __sub__(self, other):
        return Vector(
            x = self.x - other.x,
            y = self.y - other.y,
            z = self.z - other.z,
        )

    def __add__(self, other):
        return Vector(
            x = self.x + other.x,
            y = self.y + other.y,
            z = self.z + other.z,
        )

    def interpolate(self, other, t):
        return self + (other - self) * t

    @property
    def length(self):
        return math.sqrt(
            self.x * self.x +
            self.y * self.y +
            self.z * self.z
        )

    def scale(self, value):
        length = self.length
        factor = value/length
        return self * factor

    def __repr__(self):
        return 'Vector(%05.3f, %05.3f, %05.3f)' % (self.x, self.y, self.z)

class Quaternion(object):
    def __init__(self, x=0.0, y=0.0, z=0.0, w=1.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
    
    def __iter__(self):
        return iter((self.x, self.y, self.z, self.w))

    def interpolate(self, other, t):
        tmp = Quaternion()

        cosom = self.x*other.x + self.y*other.y + self.z*other.z + self.w*other.w
        if cosom < 0:
            cosom = -cosom
            tmp.x = -other.x
            tmp.y = -other.y
            tmp.z = -other.z
            tmp.w = -other.w
        else:
            tmp.x = other.x
            tmp.y = other.y
            tmp.z = other.z
            tmp.w = other.w
        
        if 0:
            omega = math.acos(cosom)
            sinom = math.sin(omega)
            scale0 = math.sin((1.0-t) * omega) / sinom
            scale1 = math.sin(t*omega) / sinom
        else:
            scale0 = 1.0 - t
            scale1 = t

        return Quaternion(
            x = scale0 * self.x + scale1 * tmp.x,
            y = scale0 * self.y + scale1 * tmp.y,
            z = scale0 * self.z + scale1 * tmp.z,
            w = scale0 * self.w + scale1 * tmp.w,
        )

class Matrix(object):
    def __init__(self, data=None):
        if data:
            self.data = data
        else:
            self.data = [
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0,
            ]

    def __getitem__(self, pos):
        if isinstance(pos, tuple):
            x, y = pos
            return self.data[x+y*4]
        else:
            return self.data[pos]
    
    def __setitem__(self, (x,y), value):
        self.data[x+y*4] = value

    def get_position(self):
        return Vector(
            x = self[0,3],
            y = self[1,3],
            z = self[2,3],
        )
    def set_position(self, value):
        self[0,3], self[1,3], self[2,3] = value
    position = property(get_position, set_position)

    def get_rotation(self):
        return self.data[:12]
    def set_rotation(self, value):
        self.data[:12] = value
    rotation = property(get_rotation, set_rotation)

    def get_quaternion(self):
        q = [0,0,0,0]
        m = self
        tr = m[0,0] + m[1,1] + m[2,2]

        next = [1,2,0]
        if tr > 0.0:
            s = (tr + 1.0) ** 0.5
            q[3] = s/2.0
            s = 0.5/s
            q[0] = (m[1,2] - m[2,1]) * s
            q[1] = (m[2,0] - m[0,2]) * s
            q[2] = (m[0,1] - m[1,0]) * s
        else:
            i = 0
            if m[1,1] > m[0,0]:
                i = 1
            if m[2,2] > m[i,i]:
                i = 2
            j = next[i]
            k = next[j]

            s = (m[i,i] - (m[j,j] + m[k,k]) + 1.0) ** 0.5
            q[i] = s * 0.5
            if s != 0.0:
                s = 0.5/s
            q[3] = (m[j,k] - m[k,j]) * s
            q[j] = (m[i,j] + m[j,i]) * s
            q[k] = (m[i,k] + m[k,i]) * s

        return Quaternion(*q)
    
    def set_quaternion(self, quaternion):
        m = self
        qx, qy, qz, qw = quaternion

        x2 = qx + qx
        y2 = qy + qy
        z2 = qz + qz
        xx = qx * x2
        xy = qx * y2
        xz = qx * z2
        yy = qy * y2
        yz = qy * z2
        zz = qz * z2
        wx = qw * x2
        wy = qw * y2
        wz = qw * z2
        
        m[0,0] = 1.0 - (yy+zz)
        m[1,0] = xy - wz
        m[2,0] = xz + wy
        m[3,0] = 0.0

        m[0,1] = xy + wz
        m[1,1] = 1.0 - (xx+zz)
        m[2,1] = yz - wx
        m[3,1] = 0.0 

        m[0,2] = xz - wy
        m[1,2] = yz + wx
        m[2,2] = 1.0 - (xx+yy)
        m[3,2] = 0.0
        
        return m
    quaternion = property(get_quaternion, set_quaternion)

    def interpolate(self, other, t):
        m = Matrix()
        m.position = self.position.interpolate(other.position, t)
        m.quaternion = self.quaternion.interpolate(other.quaternion, t)
        return m

    def __mul__(self, vector):
        return Vector(
            self[0,0]*vector.x + self[1,0]*vector.y + self[2,0]*vector.z + self[3,0],
            self[0,1]*vector.x + self[1,1]*vector.y + self[2,1]*vector.z + self[3,1],
            self[0,2]*vector.x + self[1,2]*vector.y + self[2,2]*vector.z + self[3,2],
        ) 

    def __iter__(self):
        return iter(self.data)
    
    def rotate(self, vector):
        ch = math.cos(vector.x)
        sh = math.sin(vector.x)
        ca = math.cos(vector.y)
        sa = math.sin(vector.y)
        cb = math.cos(vector.z)
        sb = math.sin(vector.z)

        self[0,0] = ch * ca
        self[1,0] = sh * sb - ch * sa * cb
        self[2,0] = ch * sa * sb + sh * cb
        self[0,1] = sa
        self[1,1] = ca * cb
        self[2,1] = -ca * sb
        self[0,2] = -sh * ca
        self[1,2] = sh * sa * cb + ch * sb
        self[2,2] = -sh * sa * sb + ch * cb
