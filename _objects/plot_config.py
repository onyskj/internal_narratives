import matplotlib.pyplot as plt
import string
import numpy as np


class PlotSizes:
    # starting plot sizes
    def __init__(self):
        # self.ax_ts = 10  # axes title font size
        # self.ax_ts_pad = 5  # axes title padding from the figure
        # self.f_ts = 15  # figure title font size (suptitle)
        #
        # self.ax_ls = 7  # axes lable size
        #
        # self.xt_ls = 4  # xtick label size
        # self.yt_ls = 4  # ytick label size
        # self.xt_rot = 0  # rotation of x ticks
        #
        # self.l_fs = 4  # legend item font size
        # self.l_tfs = 6  # legend tilte fontsize
        #
        # self.c_ls = 10  # clorbar label fontsize
        # self.c_ts = 5  # cbar tick size
        self.ax_ts = 7  # axes title font size
        self.ax_ts_pad = 5  # axes title padding from the figure
        self.f_ts = 7  # figure title font size (suptitle)

        self.ax_ls = 7  # axes lable size

        self.xt_ls = 5  # xtick label size
        self.yt_ls = 5  # ytick label size
        self.xt_rot = 0  # rotation of x ticks

        self.l_fs = 7  # legend item font size
        self.l_tfs = 7  # legend tilte fontsize

        self.c_ls = 7  # clorbar label fontsize
        self.c_ts = 5  # cbar tick size
        self.c_loc = 'right'  # location of cbar

        self.plt_dict = []
        self.tick_ms = 1.5
        self.kde_lw = 3

        plt.rcParams['axes.titlesize'] = self.ax_ts
        plt.rcParams['figure.titlesize'] = self.f_ts
        plt.rcParams['axes.titlepad'] = self.ax_ts_pad
        plt.rcParams['legend.fontsize'] = self.l_fs
        plt.rcParams['legend.title_fontsize'] = self.l_tfs
        plt.rcParams['xtick.labelsize'] = self.xt_ls
        plt.rcParams['ytick.labelsize'] = self.yt_ls
        plt.rcParams['axes.labelsize'] = self.ax_ls
        plt.rcParams["xtick.major.size"] = self.tick_ms
        plt.rcParams["ytick.major.size"] = self.tick_ms
        plt.rcParams["xtick.major.pad"] = self.tick_ms
        plt.rcParams["ytick.major.pad"] = self.tick_ms

        plt.rcParams['lines.linewidth'] = self.kde_lw

    def attr_list(self, should_print=False):
        items = self.__dict__.items()
        if should_print:
            [print(f"attribute: {k}    value: {v}") for k, v in items]

        return items


class PlotConfig:
    def __init__(self, fw=180):
        self.onerow = False
        self._plot_sizes = PlotSizes()  # inherit default rc sizes from PlotSizes

        plt.rcParams['font.family'] = 'sans-serif'
        self.c = 1  # n columns
        self.r = 1  # n rows

        self.dpi_val = 300
        self.mlt = 1  # scale for figsize

        # misc settings
        self.kde_lw = 3  # denisty plot line width
        self.annot_fs = 5  # heatmap annotation fontsize
        self.annot_p_fs = 7  # other annotations on the plot
        self.shrink = 0.7  # shrink colour bar
        self.pad = 0.1  # pad colour bar

        # boxplot settings
        self.box_lw = 0.5
        self.box_fliersize = 0
        self.box_width = 0.8
        self.box_colour = 'black'
        self.box_gap = 0.125


        # dot settings
        self.dot_lw = 0
        self.dot_size = 1.5
        self.dot_alpha = 0.7
        self.dot_jitter=0.05

        # line settings
        self.lw = 1.5

        # heatmap settings
        self.pos_heatmap = 'YlOrRd'

        # fig sizes
        self.fw = fw / 10 / 2.54  # 180 mm defualt in inches

        # colorbar ranges for covariance and factor analysis
        self.vmin_cov = None
        self.vmax_cov = None
        self.vmin_fa = None
        self.vmax_fa = None
        self.vmin_fa_rot = None
        self.vmax_fa_rot = None

        # x-axis length
        self.xmax = 1  # x-axis range max
        self.n_qs = None  # number of questions in questionnaire

        # axes stuff
        self.t = 'Panel Title'  # title
        self.axes = None  # axes array
        self._ax = None  # axis instaces
        self.i = None  # row coordinate
        self.j = None  # column coordinate
        self.plab_offset = 0

        self._figsize = None  # figure size
        self._tick_unit = None  # tick unit

        # panel labels (x,y offeset, font size)
        self._p_labs_org = np.array(
            list(string.ascii_uppercase + string.ascii_lowercase + string.ascii_uppercase + string.ascii_lowercase))
        self._p_labs = None  # to be reshaped into grid
        self.p_lab_spec = [-0.125, 1.1, 6]  # x,y loc and fontsize


    @property
    def p_labs(self):
        # reshape to be in a grid
        self._p_labs = self._p_labs_org[self.plab_offset:self.plab_offset + self.r * self.c].reshape(self.r, self.c)
        if self.onerow:
            self._p_labs = self._p_labs.reshape(1, -1)

        return self._p_labs

    # @property
    # def figsize(self):
    #     self._figsize = (4 * self.mlt * self.c, 3 * self.mlt * self.r)
    #     return self._figsize

    @property
    def tick_unit(self):
        # spacing for ticks
        self._tick_unit = int(self.xmax / 5)
        return self._tick_unit

    @property
    def ax(self):
        if self.i is not None and self.j is not None:
            if len(self.axes.shape) > 1:
                self._ax = self.axes[self.i, self.j]
            else:
                self._ax = self.axes[self.j]
        # elif self.onerow:
        #     self._ax = self.axes[self.i]

        return self._ax

    def ax_ts(self, value, by=1):
        # set axes title size
        self._plot_sizes.ax_ts = value
        plt.rcParams['axes.titlesize'] = self._plot_sizes.ax_ts
        self._plot_sizes.f_ts = self._plot_sizes.ax_ts * by
        plt.rcParams['figure.titlesize'] = self._plot_sizes.f_ts

    def ax_ts_pad(self, value):
        # set axes title padding from main figure
        self._plot_sizes.ax_ts_pad = value
        plt.rcParams['axes.titlepad'] = self._plot_sizes.ax_ts_pad

    def l_fs(self, value, by=1):
        # set legend and legend title fontsize
        self._plot_sizes.l_fs = value
        plt.rcParams['legend.fontsize'] = self._plot_sizes.l_fs
        self._plot_sizes.l_tfs = self._plot_sizes.l_fs * by
        plt.rcParams['legend.title_fontsize'] = self._plot_sizes.l_tfs

    def xyt_ls(self, x_val=None, y_val=None):
        # set x and y tick labelsizes
        if x_val is not None:
            self._plot_sizes.xt_ls = x_val
            plt.rcParams['xtick.labelsize'] = self._plot_sizes.xt_ls
            if self.ax is not None:
                self.ax.tick_params(axis='x', labelsize=self._plot_sizes.xt_ls)

        if y_val is not None:
            self._plot_sizes.yt_ls = y_val
            plt.rcParams['ytick.labelsize'] = self._plot_sizes.yt_ls
            if self.ax is not None:
                self.ax.tick_params(axis='y', labelsize=self._plot_sizes.yt_ls)

    def ax_ls(self, value):
        # set axes labelsize
        self._plot_sizes.ax_ls = value
        plt.rcParams['axes.labelsize'] = self._plot_sizes.ax_ls

    # methods_list = [method for method in dir(dataset_objects) if callable(
    #     getattr(dataset_objects, method)) and not method.startswith("__")]
    # MethodWanted = 'children'
    # getattr(ObjectToApply, MethodWanted)()
