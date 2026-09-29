# 用法: python3 render_chunk.py <时间轴.py> <起始帧> <结束帧> <输出.mp4>
# 时间轴文件需定义: MOV（原片路径）、N_SRC（原片 60fps 帧数）、SRC_HDR（True/False）、seq()
import sys, os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
seq_path, i0, i1, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
spec = importlib.util.spec_from_file_location('seqmod', seq_path); m = importlib.util.module_from_spec(spec)
sys.path.insert(0, os.path.dirname(os.path.abspath(seq_path)))
import comp4k
spec.loader.exec_module(m)
comp4k.MOV = os.path.expanduser(m.MOV); comp4k.SRC_HDR = getattr(m, 'SRC_HDR', True)
comp4k.render_chunk(m.seq(), out, 0.0, i0, i1, n_src=m.N_SRC)
