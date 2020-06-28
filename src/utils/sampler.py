import random
import os
import sys
import numpy as np
from scipy.sparse import csr_matrix


def HERec_gen_neighbour(g_hin, mp, temp_file):
    if len(mp) == 5:
        gen_neighbour_five(g_hin, mp, temp_file)
    elif len(mp) == 3:
        gen_neighbour_three(g_hin, mp, temp_file)


def gen_neighbour_three(g_hin, mp, temp_file):
    try:
        if mp[0] != mp[2]:
            raise NameError("The metapath is not symmetric!")
    except NameError:
        print("The metapath is not symmetric!")
    relation = g_hin.relation_dict[mp[0] + '-' + mp[1]]
    n1 = len(g_hin.node[mp[0]])
    n2 = len(g_hin.node[mp[1]])
    csr_mtx = re2mtx(relation, n1, n2)
    mtx = csr_mtx * csr_mtx.transpose()
    print(mtx.shape)
    temp_file += mp + ".txt"
    write2file(mtx, temp_file)


def gen_neighbour_five(g_hin, mp, temp_file):
    try:
        if mp[0] != mp[4] or mp[1] != mp[3]:
            raise NameError("The metapath is not symmetric!")
    except NameError:
        print("The metapath is not symmetric!")
    relation1 = g_hin.relation_dict[mp[0] + '-' + mp[1]]
    relation2 = g_hin.relation_dict[mp[1] + '-' + mp[2]]
    n1 = len(g_hin.node[mp[0]])
    n2 = len(g_hin.node[mp[1]])
    n3 = len(g_hin.node[mp[2]])
    mtx1 = re2mtx(relation1, n1, n2)
    mtx2 = re2mtx(relation2, n2, n3)
    mtx1_2 = mtx1 * mtx2
    mtx = mtx1_2 * mtx1_2.transpose()
    print(mtx.shape)
    temp_file += mp + ".txt"
    write2file(mtx, temp_file)


def re2mtx(relation, n1, n2):
    row = []
    col = []
    for i in relation:
        for j in relation[i]:
            row.append(int(i))
            col.append(int(j))
    data = np.ones(len(row))
    return csr_matrix((data, (row, col)), shape=(n1, n2))


def write2file(mtx, file):
    print('writing to file...')
    total = 0
    with open(file, 'w') as outfile:
        for i in range(mtx.shape[0]):
            ind = mtx[i].indices
            key = mtx[i].data
            for ix in range(len(ind)):
                if i != ind[ix]:
                    outfile.write(str(i) + '\t' + str(ind[ix]) + '\t' + str(int(key[ix])) + '\n')
                    total += 1
    print(str(total))



def mp_based_random_walk(num_walks, walk_length, mode, data_source, outfilename):
    # random.seed(2019)
    assert mode[0]==mode[-1] # MP based RW is only applicable for metapaths with same source and target nodes.

    relations = []
    for i in range(len(mode) - 1):
        relations.append(data_source.relation_dict[mode[i] + '-' + mode[i + 1]])
    start_list = data_source.node[mode[0]]
    with open(outfilename, 'w') as outfile:
        for start_node in sorted(start_list):
            for _ in range(0, int(num_walks)):
                outline = mode[0] + start_node
                current_node = start_node
                l, r = 1, 1
                while l <= walk_length:
                    current_node = random.choice(relations[r - 1][current_node])
                    outline += " " + mode[r] + current_node
                    r = r + 1 if r + 1 < len(mode) else 1
                    l += 1
                outfile.write(outline + "\n")


# def random_walk_three(num_walks, walk_length, mode, data_source, outfilename):
#     relation1 = data_source.relation_dict[mode[0] + '-' + mode[1]]
#     relation2 = data_source.relation_dict[mode[1] + '-' + mode[2]]
#     start_list = data_source.node[mode[0]]
#
#     odd = int(walk_length) % 2
#     num_length = int(int(walk_length) / 2)
#     with open(outfilename, 'w') as outfile:
#
#         for i in start_list:
#             start_node = i
#             for j in range(0, int(num_walks)):
#                 outline = mode[0] + start_node
#                 current_node = start_node
#                 for index in range(0, num_length - 1):
#                     current_node = random.choice(relation1[current_node])  # relation1
#                     outline += " " + mode[1] + current_node
#                     current_node = random.choice(relation2[current_node])  # relation2
#                     outline += " " + mode[2] + current_node
#                 if (odd == 0):
#                     current_node = random.choice(relation1[current_node])
#                     outline += " " + mode[1] + current_node
#                 outfile.write(outline + "\n")
#
#
# def random_walk_five(num_walks, walk_length, mode, data_source, outfilename):
#     relation1 = data_source.relation_dict[mode[0] + '-' + mode[1]]
#     relation2 = data_source.relation_dict[mode[1] + '-' + mode[2]]
#     relation3 = data_source.relation_dict[mode[2] + '-' + mode[3]]
#     relation4 = data_source.relation_dict[mode[3] + '-' + mode[4]]
#     start_list = data_source.node[mode[0]]
#
#     num_length = int(int(walk_length) / 4)
#     with open(outfilename, 'w') as outfile:
#         for i in start_list:
#             start_node = i
#             for j in range(0, num_walks):
#                 outline = mode[0] + start_node
#                 current_node = start_node
#                 for index in range(0, num_length):
#                     current_node = random.choice(relation1[current_node])  # relation1
#                     outline += " " + mode[1] + current_node
#
#                     current_node = random.choice(relation2[current_node])  # relation2
#                     outline += " " + mode[2] + current_node
#
#                     current_node = random.choice(relation3[current_node])  # relation3
#                     outline += " " + mode[3] + current_node
#
#                     current_node = random.choice(relation4[current_node])  # relation4
#                     outline += " " + mode[4] + current_node
#                 outfile.write(outline + "\n")


def hyper_edge_sample(g_hin, output_datafold, scale, tup):
    start_list = g_hin.node[tup[0]]
    need_types = tup.split('-')
    k = scale.split(':')
    k[0] = int(k[0])
    k[1] = int(k[1])
    collection = g_hin.relation_dict
    quence = []
    quence.append(need_types[0] + '-' + need_types[1])
    quence.append(need_types[1] + '-' + need_types[2])
    train = []
    validation = []

    reflect = g_hin.matrix2id_dict
    for start_type in start_list:
        start_type0 = start_type
        a = reflect[need_types[0] + start_type0]
        next_list = collection[quence[0]][start_type0]
        for next2 in next_list:
            b = reflect[need_types[1] + next2]
            if next2 not in collection[quence[1]]:
                break

            next3_list = collection[quence[1]][next2]
            for next3 in next3_list:
                c = reflect[need_types[2][0] + next3]

                l = []
                l.append(a)
                l.append(b)
                l.append(c)
                random_int = random.randint(0, 9)
                if random_int < k[0] / sum(k) * 10:
                    train.append(l)
                else:
                    validation.append(l)

    train = np.array(train)
    validation = np.array(validation)
    nums_t = []
    nums_t.append(len(g_hin.node[need_types[0]]))
    nums_t.append(len(g_hin.node[need_types[1]]))
    nums_t.append(len(g_hin.node[need_types[2]]))
    string_train = str(output_datafold) + 'train_data.npz'
    np.savez(string_train, train_data=train, nums_type=np.array(nums_t))
    string_validation = str(output_datafold) + 'test_data.npz'
    np.savez(string_validation, test_data=validation, nums_type=np.array(nums_t))


class RHINEDataProcess(object):
    def __init__(self, config, g_hin):
        self.node2id_dict = g_hin.node2id_dict
        self.find_dict = g_hin.find_dict
        self.matrix2id_dict = g_hin.matrix2id_dict
        self.adj_matrix = g_hin.adj_matrix
        self.link_type = config.link_type.split("+")
        self.relation2id_dict = {}
        self.output_fold = config.temp_file

        self.write2file()

    def write2file(self):
        with open(self.output_fold + "node2id.txt", "w") as f:
            f.write(str(len(self.node2id_dict)))
            for i in self.node2id_dict:
                f.write('\n' + i + '\t' + str(self.node2id_dict[i]))
        with open(self.output_fold + "relation2id.txt", 'w') as f:
            f.write(str(len(self.link_type)))
            m = 0
            for i in self.link_type:
                self.relation2id_dict[i] = m
                f.write('\n' + i + '\t' + str(m))
                m += 1

    def generate_triples(self):
        print(
            'generating triples for relation {}...'.format(
                self.link_type))

        relation_type = self.link_type
        for r in relation_type:
            sre = self.relation2id_dict[r]
            ridx, cidx = np.nonzero(self.adj_matrix[r])
            ridx = list(ridx)
            cidx = list(cidx)
            num_triples = len(ridx)
            s = r.split('-')
            source_type, target_type = s[0], s[-1]
            with open(self.output_fold + 'train2id_' + str(r) + '.txt', 'w') as f:
                for i in range(num_triples):
                    n1 = self.find_dict[str(source_type) + str(ridx[i])]
                    id1 = self.node2id_dict[source_type + n1]
                    n2 = self.find_dict[str(target_type) + str(cidx[i])]
                    id2 = self.node2id_dict[target_type + n2]
                    w = int(self.adj_matrix[r][ridx[i], cidx[i]])
                    f.write(str(id1) + '\t' + str(id2) + '\t' + str(sre) + '\t' + str(w) + '\n')

    def merge_triples(self, relation_category):
        relation_category = relation_category.split('|')
        for rc in relation_category:
            rc = rc.split('==')
            merged_data = open(
                (str(self.output_fold) + 'train2id_' + str(rc[0]) + '.txt'), 'w+')
            relation_list = rc[1].split('+')
            line_num = 0
            content = ''
            for r in relation_list:
                for line in open(str(self.output_fold) +
                                 'train2id_' + str(r) + '.txt'):
                    content += line
                    line_num += 1
            merged_data.writelines(str(line_num) + '\n' + content)


class MetaGraphGenerator:
    def __init__(self):
        pass

    # walk length=80  walks per node=40
    def generate_random_four(self, outfilename, numwalks, walklength,
                             nodelist, relation_dict):
        mg_type = "apct"
        start_list = nodelist[mg_type[0]]
        relation1 = relation_dict["a-p"]
        relation2 = relation_dict["p-a"]
        relation3 = relation_dict["p-c"]
        relation4 = relation_dict["c-p"]

        relation5 = relation_dict["p-t"]
        relation6 = relation_dict["t-p"]

        with open(outfilename, 'w') as outfile:
            for i in start_list:
                for j in range(0, numwalks):
                    k = 0
                    current_node = mg_type[0] + i
                    outline = current_node
                    while k < walklength:
                        if (current_node[0] == mg_type[0]):
                            current_node = mg_type[1] + random.choice(relation1[current_node[1:]])
                            outline += " " + current_node
                        elif current_node[0] == mg_type[1]:
                            l1 = len(relation2[current_node[1:]])
                            l2 = len(relation3[current_node[1:]])
                            l3 = len(relation5[current_node[1:]])
                            random_int = random.randint(1, l1 + l2 + l3)
                            if random_int <= l1:
                                current_node = mg_type[0] + random.choice(relation2[current_node[1:]])
                            elif random_int <= l1 + l2:
                                current_node = mg_type[2] + random.choice(relation3[current_node[1:]])
                            else:
                                current_node = mg_type[3] + random.choice(relation5[current_node[1:]])
                            outline += " " + current_node
                        elif current_node[0] == mg_type[2]:
                            current_node = mg_type[1] + random.choice(relation4[current_node[1:]])
                            outline += " " + current_node
                        elif current_node[0] == mg_type[3]:
                            current_node = mg_type[1] + random.choice(relation6[current_node[1:]])
                            outline += " " + current_node
                        else:
                            print("error!")
                        k += 1
                    outfile.write(outline + "\n")

    def generate_random_three(self, outfilename, numwalks, walklength,
                              nodelist, relation_dict):
        mg_type = "aps"
        start_list = nodelist[mg_type[0]]
        relation1 = relation_dict["a-p"]
        relation2 = relation_dict["p-a"]
        relation3 = relation_dict["p-s"]
        relation4 = relation_dict["s-p"]

        with open(outfilename, 'w') as outfile:
            for i in start_list:
                for j in range(0, numwalks):
                    k = 0
                    current_node = mg_type[0] + i
                    outline = current_node
                    while k < walklength:
                        if (current_node[0] == mg_type[0]):
                            current_node = mg_type[1] + random.choice(relation1[current_node[1:]])
                            outline += " " + current_node
                        elif current_node[0] == mg_type[1]:
                            l1 = len(relation2[current_node[1:]])
                            l2 = len(relation3[current_node[1:]])
                            random_int = random.randint(1, l1 + l2)
                            if random_int <= l1:
                                current_node = mg_type[0] + random.choice(relation2[current_node[1:]])
                            else:
                                current_node = mg_type[2] + random.choice(relation3[current_node[1:]])
                            outline += " " + current_node
                        elif current_node[0] == mg_type[2]:
                            current_node = mg_type[1] + random.choice(relation4[current_node[1:]])
                            outline += " " + current_node
                        else:
                            print("error!")
                        k += 1
                    outfile.write(outline + "\n")


class HAN_process():
    def __init__(self, g_hin, mp_list, dataset):
        self.s = mp_list[0][0]
        g_hin.load_matrix()
        self.adj_matrix = g_hin.adj_matrix
        self.label = g_hin.load_label()
        self.matrix2id_dict = g_hin.matrix2id_dict
        self.find_dict = g_hin.find_dict
        self.mp_list = mp_list.split("|")
        self.dataset = dataset
        self.n_nodes = len(g_hin.node[self.s])
        g_hin.load_fea()
        self.feature = g_hin.feature


    def fea_process(self):
        dim = len(self.feature[self.s + "0"])
        fea_array = np.zeros((self.n_nodes, dim), float)
        for i in range(self.n_nodes):
            f = self.feature[self.s + str(i)]
            id = self.matrix2id_dict[self.s + str(i)]
            fea_array[id][:] = f
        return fea_array


    def data_process(self):
        truefeatures = self.fea_process()
        rownetworks = []
        for mp in self.mp_list:
            if mp[0] != self.s:
                print("mp_list error!")
                return
            if len(mp) == 3:
                mtx1 = self.adj_matrix[mp[0] + "-" + mp[1]]
                mtx = mtx1 * mtx1.transpose()
            elif len(mp) == 5:
                mtx1 = self.adj_matrix[mp[0] + "-" + mp[1]]
                mtx2 = self.adj_matrix[mp[1] + "-" + mp[2]]
                mtx3 = mtx1 * mtx2
                mtx = mtx3 * mtx3.transpose()

            mtx.setdiag(0)
            rownetworks.append(mtx.toarray())
        N = rownetworks[0].shape[0]
        if self.dataset == "dblp":
            label = [0, 1, 2, 3]
        elif self.dataset == "acm":
            label = [0, 1, 2]

        # for i in range(N):
        #     label.append(self.label[self.s + self.find_dict[self.s + str(i)]])

        al_l = np.zeros(N)
        for key, value in self.label.items():
            al_l[int(key[1:])] = value
        float_mask = np.zeros(len(al_l))
        for l in label:
            pc_c_mask = (al_l == l)
            float_mask[pc_c_mask] = np.random.permutation(np.linspace(1, 2, pc_c_mask.sum()))
        train_idx = np.where((float_mask <= 1.2) & (float_mask >= 1))[0]
        val_idx = np.where((float_mask > 1.2) & (float_mask <= 1.3))[0]
        test_idx = np.where(float_mask > 1.3)[0]

        al_l = np.array(al_l).reshape(-1, 1)
        from sklearn.preprocessing import OneHotEncoder
        ohe = OneHotEncoder()
        ohe.fit(al_l)
        y = ohe.transform(al_l).toarray()
        y = y[..., 1:]
        train_mask = self.sample_mask(train_idx, y.shape[0])
        val_mask = self.sample_mask(val_idx, y.shape[0])
        test_mask = self.sample_mask(test_idx, y.shape[0])

        y_train = np.zeros(y.shape)
        y_val = np.zeros(y.shape)
        y_test = np.zeros(y.shape)
        y_train[train_mask, :] = y[train_mask, :]
        y_val[val_mask, :] = y[val_mask, :]
        y_test[test_mask, :] = y[test_mask, :]

        print('y_train:{}, y_val:{}, y_test:{}, train_idx:{}, val_idx:{}, test_idx:{}'.format(y_train.shape,
                                                                                              y_val.shape,
                                                                                              y_test.shape,
                                                                                              train_idx.shape,
                                                                                              val_idx.shape,
                                                                                              test_idx.shape))

        truefeatures_list = [truefeatures, truefeatures, truefeatures]
        return rownetworks, truefeatures_list, y_train, y_val, y_test, train_mask, val_mask, test_mask

    def sample_mask(self, idx, l):
        """Create mask."""
        mask = np.zeros(l)
        mask[idx] = 1
        return np.array(mask, dtype=np.bool)


def Hegan_read_graph(g_hin):
    graph = {}
    i = -1
    for relation in g_hin.relation_dict:
        i = i + 1
        type1 = relation[0]
        type2 = relation[2]
        for src in g_hin.relation_dict[relation]:
            source_node = int(g_hin.node2id_dict[type1 + src])
            for tar in g_hin.relation_dict[relation][src]:
                target_node = int(g_hin.node2id_dict[type2 + tar])

                if source_node not in graph:
                    graph[source_node] = {}

                if i not in graph[source_node]:
                    graph[source_node][i] = []

                graph[source_node][i].append(target_node)

    n_node = len(g_hin.node2id_dict)
    # print relations
    return n_node, len(g_hin.relation_dict), graph
