import sys
import os

# Allow `from pawpal_system import ...` to work when pytest is run from any directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
