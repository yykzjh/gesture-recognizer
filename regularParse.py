

class Node:
    nextString = []
    nextIndex = []
    end = False
    

def input_regular():
    with open('./regular.txt','r',encoding='utf-8') as fin: #读入语法规则文件
        #转换为二维列表形式
        regularList = [] #定义语法规则的二维列表
        for line in fin.readlines():
            line = line.rstrip('\n')
            regularList.append(line.split())
        
        return regularList


def find(list, char):
    for index, item in enumerate(list):
        if item==char:
            return index
    return "not find"

def deal_regular(regularList):
    tree = [] #定义搜索树
    nodeTmp = Node() #实例化头结点
    nodeTmp.nextString = []
    nodeTmp.nextIndex = []
    nodeTmp.end = False
    tree.append(nodeTmp) #添加头结点到搜索树

    #生成搜索树
    for i in range(len(regularList)):
        now = 0
        j = 0
        #遍历已存在的部分
        while j<len(regularList[i]) and (regularList[i][j] in tree[now].nextString):
            tmpIndex = find(tree[now].nextString,regular[i][j])
            now = int(tree[now].nextIndex[tmpIndex])
            j += 1

        #对新的分支进行创建
        while j<len(regularList[i]):
            tmpNode = Node()
            tmpNode.nextIndex = []
            tmpNode.nextString = []
            tmpNode.end = False
            tree[now].nextString.append(regularList[i][j])
            tree[now].nextIndex.append(str(len(tree)))
            tree.append(tmpNode)
            now = len(tree)-1
            j += 1

        #对语句的结尾做上标记
        tree[now].end = True
    
    # for i in range(len(tree)):
    #     print(tree[i].nextString)
    #     print(tree[i].nextIndex)
    #     print(tree[i].end)
    #     print('\n')
    return tree



def write_tree(tree):
    with open('./regular_tree.txt', 'w',encoding='utf-8') as fout:
        fout.write(str(len(tree))+'\n')
        for i in range(len(tree)):
            fout.write(' '.join(tree[i].nextString)+'\n')
            fout.write(' '.join(tree[i].nextIndex)+'\n')
            fout.write(str(tree[i].end)+'\n')



if __name__ == "__main__":

    regular = input_regular() #输入语法规则

    tree = deal_regular(regular) #生成搜索树

    write_tree(tree) #输出搜索树到文件


