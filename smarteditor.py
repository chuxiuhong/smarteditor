#!/usr/bin/python
# -*- coding: utf-8 -*-
import PyQt4
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtCore
import sys
import pickle

print '===================start======================='


class Node:
    def __init__(self):
        self.value = None
        self.children = {}  # children is of type {char, Node}
        self.fre = 0
        self.father = None


def CMP(a, b):
    return b.fre - a.fre


class Trie:
    def __init__(self):
        self.root = Node()
        self.choose = []
        self.__OpenCorrect__ = 0

    def insert(self, key):  # key is of type string
        # key should be a low-case string, this must be checked here!
        node = self.root
        for char in key:
            if char not in node.children:
                child = Node()
                node.children[char] = child
                child.value = char
                child.father = node
                node = child
            else:
                node = node.children[char]
        # node.value = key
        node.fre += 1

    def search(self, key):
        node = self.root
        for char in key:
            if char not in node.children:
                return None
            else:
                node = node.children[char]
        return node.value

    def display_node(self, node):
        if (node.value != None):
            print node.value
        for char in 'abcdefghijklmnopqrstuvwxyz':
            if char in node.children:
                self.display_node(node.children[char])
        return

    def fallback(self, node):
        f_char = ''
        while node != self.root:
            f_char = node.value + f_char
            node = node.father
        # print f_char
        return f_char

    def display(self):
        self.display_node(self.root)

    def find_node(self, string):
        res_node = self.root
        for i in string:
            res_node = res_node.children[i]
        return res_node

    def association(self, node):
        # 调用此函数前应该先将self.choose恢复成空列表
        if (node.value != None):
            if node.fre > 0:
                self.choose.append(node)
        for char in 'abcdefghijklmnopqrstuvwxyz':
            if char in node.children:
                self.association(node.children[char])

    def output_association(self, char):
        char = str(char).lower()
        self.choose = []
        result_list = []
        self.association(self.find_node(char))
        self.choose.sort(cmp=CMP)
        if len(self.choose) > 0:
            for i in self.choose:
                result_list.append(self.fallback(i))
        if self.__OpenCorrect__ == 0:
            result_list.insert(1, self.correct(char))
            # print 'result_list',result_list
        return result_list

    def correct(self, string):
        self.choose = []
        p = self.find_node(string[:-1])
        self.association(p)
        self.choose.sort(cmp=CMP)
        if len(self.choose) > 1:
            return self.fallback(self.choose[0])


def train(trie, path):
    # f = open(r'big2.txt')
    f = open(path)
    word = f.read()
    f.close()
    word = word.split(' ')
    for i in word:
        trie.insert(i)


trie = Trie()
trie.__OpenCorrect__ = 0


def save_model(T):
    f1 = open("trie.pkl", 'wb')
    pickle.dump(T, f1)
    f1.close()


def load_model(path):
    f2 = open(path, 'rb')
    trie = pickle.load(f2)
    f2.close()


print '================= END ====================='


class UI(QDialog):
    def __init__(self, parent=None):
        super(UI, self).__init__(parent)
        QSList = QStringList()
        # default
        # QSList<<'One'<<'Tow'<<'Three'<<'Four'<<'Five'
        # instance of Completer class
        cmp = Completer(QSList)
        global edit
        edit = TextEdit()
        edit.setFontPointSize(80)
        edit.setCompleter(cmp)
        self.setWindowTitle(u"智能文本编辑器")
        button1 = QPushButton(u"训练模型")
        button2 = QPushButton(u"保存文本文件")
        button3 = QPushButton(u"打开文本文件")
        '''
        buttons = QushButton()
        '''
        '''
        定义按钮，（）内为按钮名称
        '''
        self.connect(button1, SIGNAL("clicked()"), self.get_file)
        self.connect(button2, SIGNAL("clicked()"), self.func2)
        self.connect(button3, SIGNAL("clicked()"), self.func3)
        '''
        关联按钮与函数格式同上，触发为clicked()单击，最后一个参数为
        类内函数
        '''
        layout = QGridLayout()
        layout.addWidget(edit, 0, 1, 1, 5)
        layout.addWidget(button1, 2, 1)
        layout.addWidget(button2, 2, 3)
        layout.addWidget(button3, 2, 5)
        '''
        按钮布局
        '''
        self.setLayout(layout)
        self.center()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def get_file(self):
        s = QFileDialog.getOpenFileName(self, "Open file dialog", "/", "TXT Files(*.txt)")
        train(trie, s)

    def func2(self):
        s = QFileDialog.getSaveFileName(self, "文件保存", "C:/", "All Files (*);Text Files (*.txt)")
        f = open(s, 'w')
        f.write(edit.toPlainText())
        f.close()

    def func3(self):
        s = QFileDialog.getOpenFileName(self, "Open file dialog", "/", "TXT Files(*.txt)")
        f = open(s)
        edit.setText(PyQt4.QtCore.QString(f.read()))
        f.close()


class TextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)
        self.cmp = None
        self.p = ''
        self.count = 0

    def setCompleter(self, completer):
        if self.cmp:
            self.disconnect(self.cmp, 0, 0)
        self.cmp = completer
        if (not self.cmp):
            return
        self.cmp.setWidget(self)
        self.cmp.setCompletionMode(QCompleter.PopupCompletion)
        self.cmp.setCaseSensitivity(Qt.CaseInsensitive)
        self.connect(self.cmp, SIGNAL('activated(QString)'), self.insertCompletion)

    def completer(self):
        return self.cmp

    def insertCompletion(self, string):

        # get cursor position
        tc = self.textCursor()
        # selectd ranges
        tc.movePosition(QTextCursor.StartOfWord, QTextCursor.KeepAnchor)

        # replace selected ranges
        tc.insertText(string)
        self.p += str(string)
        # set cursor pos back to original pos
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def keyPressEvent(self, e):
        '''
        if e.key() != Qt.Key_Backspace:
            self.p = self.p + e.text()
            self.count+=1
            print 'yes'
        else:
            self.p = self.p[:-1]
            self.count-=1
        '''
        print 'p  ', self.p
        print 'pressed >> ', e.text()
        if (self.cmp and self.cmp.popup().isVisible()):
            if e.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                e.ignore()
                return

        isShortcut = ((e.modifiers() & Qt.ControlModifier) and e.key() == Qt.Key_E)
        if (not self.cmp or not isShortcut):
            super(TextEdit, self).keyPressEvent(e)

        ctrlOrShift = e.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if (not self.cmp or (ctrlOrShift and e.text().isEmpty())):
            return

        eow = QString("~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=")
        hasModifier = (e.modifiers() != Qt.NoModifier) and not ctrlOrShift
        completionPrefix = self.textUnderCursor()
        # hide popup while matching invalid cases
        if (not isShortcut and (hasModifier or e.text().isEmpty() or completionPrefix.length() < 1
                                or eow.contains(e.text().right(1)))):
            self.cmp.popup().hide()
            return

        self.cmp.update(completionPrefix)
        self.cmp.popup().setCurrentIndex(self.cmp.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self.cmp.popup().sizeHintForColumn(0)
                    + self.cmp.popup().verticalScrollBar().sizeHint().width())
        word = self.p.split(' ')[:-1]
        self.p = ''
        for k in xrange(len(word)):
            self.p += word[k]
        print 'self.p=', self.p
        self.cmp.complete(cr)


class Completer(QCompleter):
    def __init__(self, stringlist, parent=None):
        super(Completer, self).__init__(parent)
        self.stringlist = stringlist
        self.setModel(QStringListModel())

    # update function will trigger while the text has been modified
    def update(self, completionText):
        # generate a new QStringList instance
        qsList = QStringList()

        # generate hint lists which returns by customatic definitions
        newList = genMyStrList(completionText)
        for item in newList:
            qsList.append(item)

        self.stringlist = qsList
        # filteredList = self.stringlist.filter(completionText, Qt.CaseInsensitive)
        self.model().setStringList(self.stringlist)
        self.popup().setCurrentIndex(self.model().index(0, 0))


# the function below defined a way to generate a string list
def genMyStrList(key):
    my_str_list = trie.output_association(key)
    return my_str_list


def main():
    app = QApplication(sys.argv)
    app.processEvents()
    form = UI()
    form.show()
    # splash.finish(form)
    app.exec_()
    window = QMainWindow()
    window.statusBar().showMessage('Yuan Ziqi')
    menubar = window.menuBar

    window.setWindowTitle('Auto Complete Demo')
    window.resize(400, 200)
    window.move(400, 100)

    edit = TextEdit()
    edit.setFontPointSize(40)
    edit.setCompleter(cmp)
    # bt = addbutton()
    # window.addDockWidget(bt)
    window.setCentralWidget(edit)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    print 'app is running successfully'
    main()
