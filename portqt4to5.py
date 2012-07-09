#!/usr/bin/env python

import os, sys
import subprocess

qt4to5Binary = "~/dev/build/qtbase/llvm/bin/qt4to5"
cmakeBinary = "cmake"

if os.popen("git diff").read():
    print "Error: must start with a clean working dir"
    sys.exit(1)

# Utility functions
def execCommand(command):
  print "RUNNING", command
  subprocess.Popen(command, shell=True).wait()

def createCommit(message):
  if not os.popen("git diff").read():
    return
  execCommand("git commit -am \"" + message + "\"")
  execCommand("git show --stat")


def setupEnv():

  os.mkdir("porting")
  os.chdir("porting")

  execCommand(cmakeBinary + ' .. -DCMAKE_EXPORT_COMPILE_COMMANDS=TRUE')
  # Consider running make here to ensure that required generated files get generated (moc and ui files)

  os.chdir("..")

if not os.path.exists("porting/compile_commands.json"):
  setupEnv()


# Porting functions
def renameMethod(className, oldName, newName):
  renameClass = ""
  if className:
    renameClass = " -rename-class=::" + className
  execCommand("git grep -lw " + oldName + " | xargs " + qt4to5Binary + renameClass + " -rename-old=" + oldName + " -rename-new=" + newName + " " + os.getcwd() + " " + os.getcwd() + "/porting")
  createCommit("Port uses of " + className + "::" + oldName + " to " + newName)

def portQtEscape():
  execCommand("git grep -lw Qt::escape | xargs " + qt4to5Binary + " -port-qt-escape -create-ifdefs " + " " + os.getcwd() + " " + os.getcwd() + "/porting")
  createCommit("Port from Qt::escape to QString::toHtmlEscaped")

def portQMetaMethodSignature():
  execCommand("git grep -l \"\\.signature()\" | xargs " + qt4to5Binary + " -port-qmetamethod-signature -create-ifdefs " + os.getcwd() + " " + os.getcwd() + "/porting")
  createCommit("Port from QMetaMethod::signature to methodSignature")

def replaceQVariantTemplateFunctions():
  execCommand("git grep -l qVariantCanConvert | xargs sed -i 's|qVariantCanConvert<\\(\\s*[^>\\]\\+\\)>\\s*(\\s*\\([^)]\\+\\))|\\2.canConvert<\\1>()|'")
  execCommand("git grep -l canConvert | xargs sed -i 's| \\.canConvert|.canConvert|'")
  execCommand("git grep -l qVariantValue | xargs sed -i 's|qVariantValue<\\(\\s*[^>\\]\\+\\)>\\s*(\\s*\\([^)]\\+\\))|\\2.value<\\1>()|'")
  execCommand("git grep -l \" .value\" | xargs sed -i 's| \\.value|.value|'")
  createCommit("Port from QVariant free-functions to template methods")

def replaceQObjectTemplateFunctions():
  execCommand("git grep -l qFindChild | xargs sed -i 's|qFindChild<\\(\\s*[^>\\]\\+\\)>\\s*(\\s*\\([^)]\\+\\))|\\2->findChild<\\1>()|'")
  execCommand("git grep -l findChild | xargs sed -i 's| ->findChild|->findChild|'")
  execCommand("git grep -l qFindChildren | xargs sed -i 's|qFindChildren<\\(\\s*[^>\\]\\+\\)>\\s*(\\s*\\([^)]\\+\\))|\\2->findChildren<\\1>()|'")
  execCommand("git grep -l findChildren | xargs sed -i 's| ->findChildren|->findChildren|'")
  createCommit("Port from QObject free-functions to template methods")

def portAtomics():
  execCommand("git grep -lw QAtomicInt | xargs " + qt4to5Binary + " -port-atomics -create-ifdefs " + os.getcwd() + " " + os.getcwd() + "/porting")
  createCommit("Port implicit casts of QAtomicInt and QAtomicPointer")

def portViews():
  execCommand("git grep -lw dataChanged  | xargs " + qt4to5Binary + " -port-qabstractitemview-datachanged -create-ifdefs " + os.getcwd() + " " + os.getcwd() + "/porting")
  createCommit("Port QAbstractItemView::dataChanged")

def portEnum(scope, printedScope, oldName, newName):
  execCommand("git grep -lw " + oldName + " | xargs " + qt4to5Binary + " -rename-enum=" + scope + " --create-ifdefs -rename-old=" + oldName + " -rename-new=" + printedScope + "::" + newName + " " + os.getcwd() + " " + os.getcwd() + "/porting")
  createCommit("Port  uses of " + printedScope + "::" + oldName + " to " + newName)

def portQImageText():
  execCommand("git grep -l \"text(.\\+0\\s*)\" | xargs " + qt4to5Binary + " -port-qimage-text " + os.getcwd() + " " + os.getcwd() + "/porting")
  execCommand("git grep -l \"setText(.\\+0.\\+)\" | xargs " + qt4to5Binary + " -port-qimage-text " + os.getcwd() + " " + os.getcwd() + "/porting")
  createCommit("Port uses of QImage::text and QImage::setText.")

## Pre-porting steps. These can be done before porting to Qt 5 (eg port away from deprecated methods).

def portFromQt3Support():
  renameMethod("QTransform", "det", "determinant")
  renameMethod("QWidget", "setShown", "setVisible")
  renameMethod("QWidget", "setIcon", "setWindowIcon")

def portFromQt4Deprecated():
  portQImageText()

  portViews()

  renameMethod("QPaintDevice", "numColors", "colorCount")
  renameMethod("QImage", "numColors", "colorCount")
  renameMethod("QImage", "setNumColors", "setColorCount")

  renameMethod("", "qMemCopy", "memcpy")

  renameMethod("QImage", "numBytes", "byteCount")

  renameMethod("QDate", "setYMD", "setDate")
  renameMethod("QRegion", "unite", "united")
  renameMethod("QRect", "unite", "united")
  renameMethod("QRegion", "intersect", "intersected")
  renameMethod("QRect", "intersect", "intersected")
  renameMethod("QSslCertificate", "alternateSubjectNames", "subjectAlternativeNames")

  renameMethod("QFont", "removeSubstitution", "removeSubstitutions")

  renameMethod("QHeaderView", "setMovable", "setSectionsMovable")
  renameMethod("QHeaderView", "setClickable", "setSectionsClickable")
  renameMethod("QHeaderView", "setResizeMode", "setSectionResizeMode")

  replaceQVariantTemplateFunctions()
  replaceQObjectTemplateFunctions()

## Porting steps

def port4to5():
  portQMetaMethodSignature()
  #portAtomics()

##Post porting. Porting away from deprecated API

def portFromQt5Deprecated():
  portQtEscape()
  portEnum("QSsl::SslProtocol", "QSsl", "TlsV1", "TlsV1_0")


# These function invokations do the actual porting.

portFromQt3Support()
portFromQt4Deprecated()
port4to5()
portFromQt5Deprecated()
