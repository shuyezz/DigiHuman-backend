import os;
import sys;

def init_path():
    sys.path.append(os.path.join(os.path.dirname(__file__), "./models"));
    #sys.path.append(os.path.join(os.path.dirname(__file__), "./models/cemotion"));