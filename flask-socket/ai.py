import time
from numpy import *

# 震惊!传说中价值百万的AI代码
######## 原始数据集 ########

p_s = [[1, 1, 2], [1, 2, 3], [2, 1, 6], [5, 2, 5], [8, 3, 4], [7, 7, 4], [7, 7, 7], [
    13, 8, 3], [6, 10, 11], [13, 0, 17], [14, 7, 12]]              # 用来训练的数据集 x
t_s = [[2], [6], [12], [50], [96], [196], [343],
       [312], [660], [0], [1176]]   # 用来训练的数据集 y

p_t = [[6, 9, 1017], [2, 3, 4], [5, 9, 10]]      # 用来测试的数据集 x_test
t_t = [[54918], [24], [450]]               # 用来测试的数据集 对应的实际结果 y_test

######## 超参数设定 ########

n_epoch = 2                # 训练次数

HNum = 2                   # 各层隐藏层节点数

HCNum = 2                  # 隐藏层层数

AFKind = 3                 # 激励函数种类
emax = 0.01                # 最大允许均方差根
LearnRate = 0.01           # 学习率

######## 中间变量设定 ########
TNum = 7                   # 特征层节点数 (特征数)

SNum = len(p_s)            # 样本数

INum = len(p_s[0])         # 输入层节点数（每组数据的维度）
ONum = len(t_s[0])         # 输出层节点数（结果的维度）
StudyTime = 0              # 学习次数
KtoOne = 0.0               # 归一化系数
e = 0.0                    # 均方差跟

######################################################### 主要矩阵设定 ######################################################

I = zeros(INum)

Ti = zeros(TNum)
To = zeros(TNum)

Hi = zeros((HCNum, HNum))
Ho = zeros((HCNum, HNum))

Oi = zeros(ONum)
Oo = zeros(ONum)

Teacher = zeros(ONum)

u = 0.2*ones((TNum, HNum))                  # 初始化 权值矩阵u
w = 0.2*ones(((HCNum-1, HNum, HNum)))        # 初始化 权值矩阵w
v = 0.2*ones((HNum, ONum))                  # 初始化 权值矩阵v

dw = zeros((HCNum-1, HNum, HNum))

Hb = zeros((HCNum, HNum))
Ob = zeros(ONum)

He = zeros((HCNum, HNum))
Oe = zeros(ONum)

p_s = array(p_s)
t_s = array(t_s)
p_t = array(p_t)

################################# 时间参数 #########################################

time_start = 0.0
time_gyuyihua = 0.0
time_nnff = 0.0
time_nnbp = 0.0
time_begin = 0.0

time_start2 = 0.0

time_nnff1 = 0.0
time_nnff2 = 0.0
time_nnbp_v = 0.0
time_nnbp_w = 0.0
time_nnbp_u = 0.0
time_nnbp_b = 0.0


######################################################### 方法 #######################################################

def Calcu_KtoOne(p, t):                         # 确定归一化系数
    p_max = p.max()
    t_max = t.max()
    return max(p_max, t_max)


def trait(p):                                  # 特征化
    t = zeros((p.shape[0], TNum))
    for i in range(0, p.shape[0], 1):
        t[i, 0] = p[i, 0]*p[i, 1]*p[i, 2]
        t[i, 1] = p[i, 0]*p[i, 1]
        t[i, 2] = p[i, 0]*p[i, 2]
        t[i, 3] = p[i, 1]*p[i, 2]
        t[i, 4] = p[i, 0]
        t[i, 5] = p[i, 1]
        t[i, 6] = p[i, 2]

    return t


def AF(p, kind):   # 激励函数
    t = []
    if kind == 1:   # sigmoid
        pass
    elif kind == 2:   # tanh
        pass
    elif kind == 3:    # ReLU
        return where(p < 0, 0, p)
    else:
        pass


def dAF(p, kind):   # 激励函数导数
    t = []
    if kind == 1:   # sigmoid
        pass
    elif kind == 2:   # tanh
        pass
    elif kind == 3:    # ReLU
        return where(p < 0, 0, 1)
    else:
        pass


def nnff(p, t):
    pass


def nnbp(p, t):
    pass


def train(p, t):                                # 训练

    global e
    global v
    global w
    global dw
    global u
    global I
    global Ti
    global To
    global Hi
    global Ho
    global Oi
    global Oo
    global Teacher
    global Hb
    global Ob
    global He
    global Oe
    global StudyTime
    global KtoOne

    global time_start
    global time_gyuyihua
    global time_nnff
    global time_nnbp
    global time_start2
    global time_nnff1
    global time_nnff2
    global time_nnbp_v
    global time_nnbp_w
    global time_nnbp_u
    global time_nnbp_b

    time_start = time.clock()

    e = 0.0
    p = trait(p)

    KtoOne = Calcu_KtoOne(p, t)

    time_gyuyihua += (time.clock()-time_start)

    time_start = time.clock()

    for isamp in range(0, SNum, 1):
        To = p[isamp]/KtoOne
        Teacher = t[isamp]/KtoOne

        ################ 前向 nnff #############################

        time_start2 = time.clock()
        ######## 计算各层隐藏层输入输出 Hi Ho ########

        for k in range(0, HCNum, 1):
            if k == 0:
                Hi[k] = dot(To, u)
                Ho[k] = AF(add(Hi[k], Hb[k]), AFKind)
            else:
                Hi[k] = dot(Ho[k-1], w[k-1])
                Ho[k] = AF(add(Hi[k], Hb[k]), AFKind)

        time_nnff1 += (time.clock()-time_start2)
        time_start2 = time.clock()

        ########   计算输出层输入输出 Oi Oo    ########
        Oi = dot(Ho[HCNum-1], v)
        Oo = AF(add(Oi, Ob), AFKind)

        time_nnff2 += (time.clock()-time_start2)
        time_start2 = time.clock()
        time_nnff += (time.clock()-time_start)
        time_start = time.clock()

        ################ 反向 nnbp #############################

        ######## 反向更新 v ############

        Oe = subtract(Teacher, Oo)
        Oe = multiply(Oe, dAF(add(Oi, Ob), AFKind))

        e += sum(multiply(Oe, Oe))

        #### v 梯度 ####

        dv = dot(array([Oe]), array([Ho[HCNum-1]])
                 ).transpose()              # v 的梯度

        v = add(v, dv*LearnRate)    # 更新 v

        time_nnbp_v += (time.clock()-time_start2)

        time_start2 = time.clock()

        ######## 反向更新 w #############
        He = zeros((HCNum, HNum))

        for c in range(HCNum-2, -1, -1):
            if c == HCNum-2:
                He[c+1] = dot(v, Oe)
                He[c+1] = multiply(He[c+1], dAF(add(Hi[c+1], Hb[c+1]), AFKind))

                #dw[c] = dot(array([He[c+1]]),array([Ho[c]]).transpose())
                dw[c] = dot(array([Ho[c]]).transpose(), array([He[c+1]]))
                #dw[c] = dw[c].transpose()  #@@@@@@ 若结果不理想，可尝试用此条语句

                w[c] = add(w[c], LearnRate*dw[c])

            else:
                He[c+1] = dot(w[c+1], He[c+2])
                He[c+1] = multiply(He[c+1], dAF(add(Hi[c+1], Hb[c+1]), AFKind))

                dw[c] = dot(array([Ho[c]]).transpose(), array([He[c+1]]))

                w[c] = add(w[c], LearnRate*dw[c])

        time_nnbp_w += (time.clock()-time_start2)

        time_start2 = time.clock()

        ######## 反向更新 u #############

        He[0] = dot(w[0], He[1])
        He[0] = multiply(He[0], dAF(add(Hi[0], Hb[0]), AFKind))

        du = dot(array([To]).transpose(), array([He[0]]))

        u = add(u, du)

        time_nnbp_u += (time.clock()-time_start2)

        time_start2 = time.clock()

        ######### 更新阈值 b ############

        Ob = Ob + Oe*LearnRate

        Hb = Hb + He*LearnRate

        time_nnbp += (time.clock()-time_start)

        time_start = time.clock()

        time_nnbp_b += (time.clock()-time_start2)

        time_start2 = time.clock()

    e = sqrt(e)


def predict(p):

    p = trait(p)
    p = p/KtoOne
    p_result = zeros((p.shape[0], 1))

    for isamp in range(0, p.shape[0], 1):
        for k in range(0, HCNum, 1):
            if k == 0:
                Hi[k] = dot(p[isamp], u)
                Ho[k] = AF(add(Hi[k], Hb[k]), AFKind)
            else:
                Hi[k] = dot(Ho[k-1], w[k-1])
                Ho[k] = AF(add(Hi[k], Hb[k]), AFKind)

        ########   计算输出层输入输出 Oi Oo    ########
        Oi = dot(Ho[HCNum-1], v)
        Oo = AF(add(Oi, Ob), AFKind)
        Oo = Oo*KtoOne
        p_result[isamp] = Oo
    return p_result


def main():
    time_begin = time.clock()

    for i in range(1, n_epoch, 1):
        if i % 1000 == 0:
            print('已训练 %d 千次 ,误差均方差 %f' % ((i/1000), e))
        train(p_s, t_s)
    print('训练完成，共训练 %d 次，误差均方差 %f' % (i, e))

    print('共耗时: ', time.clock()-time_begin)

    print()

    result = predict(p_t)

    print('模型预测结果 : ')
    for i in result:
        print('%.2f' % i)

    print('\n实际结果 : ')
    for i in t_t:
        print(i)
