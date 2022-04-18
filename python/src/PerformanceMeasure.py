# coding=utf-8

import math
import numpy as np


class PerformanceMeasure():
    def __init__(self, real_list=None, pred_list=None, loc=None, percentage=0.2, ranking="defect", cost="module"):
        self.real = real_list
        self.pred = pred_list
        self.loc = loc
        self.percentage = percentage
        self.ranking = ranking
        self.cost = cost

    def Performance(self):
        if (len(self.pred) != len(self.real)) or (len(self.pred) != len(self.loc) or (len(self.loc) != len(self.real))):
            print("the input lengh of the number or the density of predictive defeats are not equal to the real ones!")
            exit()

        M = len(self.real)  # total modules: M
        L = sum(self.loc)  # totol LOC: L
        P = sum([1 if i > 0 else 0 for i in self.real])  # real number of defective modules: P
        m = None  # the number of modules in top 20% LOC
        Q = sum(self.real)  # total defects: Q

        if self.ranking == "density" and self.cost == 'loc':  # sort modules by defect density in descending order, x-axis = loc
            density = [self.pred[i] / self.loc[i] if self.loc[i] != 0 else -math.inf for i in range(len(self.pred))]
            sort_axis = np.argsort(density)[::-1]
            sorted_density = np.array(density)[sort_axis]
            sorted_pred = np.array(self.pred)[sort_axis]
            sorted_real = np.array(self.real)[sort_axis]
            sorted_loc = np.array(self.loc)[sort_axis]

            locOfPercentage = self.percentage * L
            sum_ = 0
            for i in range(len(sorted_loc)):
                sum_ += sorted_loc[i]
                if sum_ > locOfPercentage:
                    m = i
                    break
                elif sum_ == locOfPercentage:
                    m = i + 1
                    break

            # calculate PMI
            PMI = m / M

        tp = sum([1 if sorted_real[j] > 0 and sorted_pred[j] > 0.5 else 0 for j in range(m)])
        fn = sum([1 if sorted_real[j] > 0 and sorted_pred[j] <= 0.5 else 0 for j in range(m)])
        fp = sum([1 if sorted_real[j] <= 0 and sorted_pred[j] > 0.5 else 0 for j in range(m)])
        tn = sum([1 if sorted_real[j] <= 0 and sorted_pred[j] <= 0.5 else 0 for j in range(m)])

        # calculate Precision
        if tp + fn + fp + tn == 0:
            Precisionx = 0
        else:
            Precisionx = (tp + fn) / m

        # calculate Recall
        if P == 0:
            Recallx = 0
        else:
            Recallx = (tp + fn) / P

        # calculate IFA
        IFA = 0
        for i in range(m):
            if sorted_real[i] > 0:
                break
            else:
                IFA += 1

        # calculate PofB
        PofB = sum([sorted_real[j] if sorted_real[j] > 0 else 0 for j in range(m)]) / Q

        return Precisionx, Recallx, IFA, PMI, PofB

    def POPT(self):
        Q = sum(self.real)  # total defects: Q

        if self.ranking == "density" and self.cost == 'loc':  # sort modules by defect density in descending order, x-axis = loc
            pred_index = [j / i if j != 0 and i != 0 else 0 for i, j in zip(self.loc, self.pred)]
            pred_index = list(np.argsort(pred_index))
            pred_index.reverse()
            xcost = self.loc
            xcostsum = sum(xcost)

        else:
            print("Error in input parameters")
            exit()

        optimal_index = [j / i if j != 0 and i != 0 else 0 for i, j in zip(xcost, self.real)]
        optimal_index = list(np.argsort(optimal_index))
        optimal_index.reverse()

        optimal_X = [0]
        optimal_Y = [0]
        for i in optimal_index:
            optimal_X.append(xcost[i] / xcostsum + optimal_X[-1])
            optimal_Y.append(self.real[i] / Q + optimal_Y[-1])

        wholeoptimal_auc = 0.
        prev_x = 0
        prev_y = 0
        for x, y in zip(optimal_X, optimal_Y):
            if x != prev_x:
                wholeoptimal_auc += (x - prev_x) * (y + prev_y) / 2.
                # print('wholeoptimalx', (x - prev_x))
                # print('wholeoptimaly', (y + prev_y))
                prev_x = x
                prev_y = y

        # print('wholeoptimalauc', wholeoptimal_auc)

        pred_X = [0]
        pred_Y = [0]
        for i in pred_index:
            pred_X.append(xcost[i] / xcostsum + pred_X[-1])
            pred_Y.append(self.real[i] / Q + pred_Y[-1])

        wholepred_auc = 0.
        prev_x = 0
        prev_y = 0
        for x, y in zip(pred_X, pred_Y):
            if x != prev_x:
                wholepred_auc += (x - prev_x) * (y + prev_y) / 2.
                # print('predx', (x - prev_x))
                # print('predy', (y + prev_y))
                prev_x = x
                prev_y = y

        # print('wholepredauc',wholepred_auc)

        optimal_index.reverse()
        mini_X = [0]
        mini_Y = [0]
        for i in optimal_index:
            mini_X.append(xcost[i] / xcostsum + mini_X[-1])
            mini_Y.append(self.real[i] / Q + mini_Y[-1])

        wholemini_auc = 0.
        prev_x = 0
        prev_y = 0
        for x, y in zip(mini_X, mini_Y):
            if x != prev_x:
                wholemini_auc += (x - prev_x) * (y + prev_y) / 2.
                # print('wholeworstpredx', (x - prev_x))
                # print('wholeworstpredy', (y + prev_y))
                prev_x = x
                prev_y = y

        # print('worstwholeauc',wholemini_auc)

        wholemini_auc = 1 - (wholeoptimal_auc - wholemini_auc)
        wholenormOPT = ((1 - (wholeoptimal_auc - wholepred_auc)) - wholemini_auc) / (1 - wholemini_auc)

        return wholenormOPT
