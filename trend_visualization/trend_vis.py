# 必要なライブラリのimport 
from  datetime import datetime

import matplotlib.pyplot as plt
from matplotlib import cm, dates, ticker
from matplotlib.backends.backend_pdf import PdfPages

def trend_vis(df, plot_list=None, fig_save_name=None, legend_loc="lower right", 
              graph_width=12.0, graph_height=3.0, x_min=None, x_max=None,
              colorbar_column=None, ver_line_list=[],
              x_major_loc=None, x_minor_loc=None, x_major_format=None):
    """
    トレンドデータを変数１つずつプロットする（初期検討用）
    x軸：時間（df.index), y軸：各変数の値
    
    Parameters
    ----------
    plot_list : list (default=None)
        プロットしたいcolumn.nameを指定。
    fig_save_name : str (default=None)
        画像を保管したい場合はファイル名を指定する（xxxx.png, yyyy.pdf 等)
    legend_loc : "str" (default="lower right")
        legend の表示位置。
    graph_widh: float or int (default=12.0)
        グラフの幅。
    graph_height : float or int (default=3.0)
        各グラフの高さ
    x_min, a_max : datetime or None (default=None)
        時間軸の左端と右端。
        Noneの場合は、df.index.min() と df.index.max()
        指定する場合は、datetime.datetime(year, month, day, hour, min)
    colorbar_column : str or None (default=None)
        None の場合は colorbarなし
        特定のカラム名（str)を指定することでカラーバー表示（表示までに約５倍時間がかかる）
    ver_line_list : list or None (default=None)
        None の場合は垂直線なし。
        listの各要素は datetime形式。
    x_major_loc, x_minor_loc: mpl.dates.~ or None (default=None)
        軸の設定。
        設定する場合は以下参照。
        * mpl.dates.DayLocator(bymonthday=None, interval=7, zn=None)
        * mpl.dates.drange(
              dstart = df.index.min(),
              dend = datetime.datetime(2021, 5, 31, 23, 59),
              delta = datetime.timedelta(days=7))
    x_major_format : mpl.dates.DateFormatter(~) or None (default=None)
        時間軸の表示方法。
        設定する場合は以下参照。
        * mpl.dates.DateFormatter("%m/%d %H:%M")
        * mpl.dates.DateFormatter("%y/%m/%d")
    
    Returns
    ----------
    None
    (グラフが返される）
    (fig_save_name に filename を指定すると、画像ファイルも作成される）
    
    
    Examples
    ----------
    1) trend_vis.trend_vis(df)
    
    2) trend_vis.trend_vis(df, colorbar_column = "target",
                           fig_save_name="sample.png")
    
    """
    def _trend_vis(_column, _ax, _idx=1):
        if colorbar_column is not None:
            mappable = _ax.scatter(df.index, df[_column], s=4, label=column,
                                  c=df[colorbar_column], cmap="coolwarm")
            cbar = fig.colorbar(mappable, ax = _ax)
            cbar.set_label(colorbar_column)
        else:
            _ax.plot(df.index, df[column], color=cm.tab10.colors[_idx%10], 
                         label=column)
            _ax.legend(loc=legend_loc)

        # 垂線
        for ver in ver_line_list:
            _ax.axvline(x=ver, color='indianred')

        # trend表示範囲の設定
        _ax.set_xlim(x_min, x_max)

        # x軸の設定
        _ax.tick_params(axis="x", rotation=60)  # 要望があれば、rotationも変数に格納
        if x_major_loc is not None:
            if type(x_major_loc) == np.ndarray:
                _ax.xaxis.set_major_locator(ticker.FixedLocator(x_major_loc))
            else:
                _ax.xaxis.set_major_locator(x_major_loc)

        if x_major_format is not None:
            _ax.xaxis.set_major_formatter(x_major_format)
        _ax.grid(alpha=0.75, linewidth=1.5)

        if x_minor_loc is not None:
            if type(x_minor_loc) == np.ndarray:
                _ax.xaxis.set_minor_locator(ticker.FixedLocator(x_minor_loc))
            else:
                _ax.xaxis.set_minor_locator(x_minor_loc)
            _ax.grid(alpha=0.75, which="minor", ls="--", lw=0.35)

        # y軸ラベルの設定
        _ax.set_ylabel(_column)
    
    
    ## __init__
    df = df.copy()
    
    # プロットするカラムを決定。 plot_list == Noneのとき、全てのカラムを選択
    if plot_list is None:
        plot_list = df.columns
    number = len(plot_list)

    # pdf作成要否判断
    if fig_save_name is not None and fig_save_name.split(".")[-1] == "pdf":
        is_save_pdf = True
        pdf = PdfPages(fig_save_name)
    else:
        is_save_pdf = False

    # グラフ描画
    if not is_save_pdf:
        fig, ax = plt.subplots(number, 1, figsize=(graph_width, graph_height*number))
        for idx, column in enumerate(plot_list):
            _trend_vis(_column=column, _ax=ax[idx], _idx=idx)

    else:
        for idx, column in enumerate(plot_list):
            fig, ax = plt.subplots(figsize=(graph_width, graph_height))
            _trend_vis(_column=column, _ax=ax, _idx=idx)
            plt.tight_layout()
            pdf.savefig(fig)
    
    if is_save_pdf:
        pdf.close()
    elif fig_save_name is not None:
        plt.tight_layout()
        plt.savefig(fig_save_name)
    