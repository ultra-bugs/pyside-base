import glob
import os

def compileUiFile(uiFile):
    """Compile a .ui file to Python code"""
    pyFile = uiFile.replace('.ui', '.py')
    os.system(f'pyside6-uic {uiFile} -o {pyFile}')
    print(f'Compiled {uiFile} -> {pyFile}')

def compileQrcFile(qrcFile):
    """Compile a .qrc file to Python code"""
    pyFile = qrcFile.replace('.qrc', '_rc.py')
    os.system(f'pyside6-rcc {qrcFile} -o {pyFile}')
    print(f'Compiled {qrcFile} -> {pyFile}')

def findFiles(pattern):
    """Find all files matching pattern"""
    basePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return glob.glob(os.path.join(basePath, '**', pattern), recursive=True)

def main():
    uiFiles = findFiles('*.ui')
    for uiFile in uiFiles:
        compileUiFile(uiFile)
    qrcFiles = findFiles('*.qrc')
    for qrcFile in qrcFiles:
        compileQrcFile(qrcFile)
if __name__ == '__main__':
    main()