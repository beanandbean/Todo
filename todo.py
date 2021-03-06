magic='--calling-python-from-bash--'
"""exec" python -E "$0" "$@" """#$magic"

if __name__ == "__main__":
    import copy, getpass, os, pickle, sys, time

    def _now():
        localTime=time.localtime()
        localTimeString="%04d-%02d-%02d %02d:%02d:%02d" % (localTime.tm_year, localTime.tm_mon, localTime.tm_mday, localTime.tm_hour, localTime.tm_min, localTime.tm_sec)
        return localTimeString

    def _todoListPath():
        # TODO: Looking back into the file tree for ".todo/list.data"
        return os.path.join(os.getcwd(), ".todo", "list.data")

    def _grabListPath():
        # TODO: Looking back into the file tree for ".todo/grab.data"
        return os.path.join(os.getcwd(), ".todo", "grab.data")

    def _todoList():
        if os.path.isfile(_todoListPath()):
            return pickle.load(open(_todoListPath()))
        else:
            return list()

    def _grabList():
        if os.path.isfile(_grabListPath()):
            return pickle.load(open(_grabListPath()))
        else:
            return list()

    def _saveTodoList(todoList):
        pickle.dump(todoList, open(_todoListPath(), "w"))
        os.chmod(_todoListPath(), 0666)

    def _saveGrabList(grabList):
        pickle.dump(grabList, open(_grabListPath(), "w"))
        os.chmod(_grabListPath(), 0666)

    def _addLine(todoList, text, detail = "", author = getpass.getuser(), more = {}):
        data = {"author": author, "time": _now(), "condition": "open", "text": text, "detail":detail, "exported": False}
        data.update(more)
        todoList.append(data)

    def _line(todoList, index):
        return " %15s %03d: [%s] %s" % ("(%s)" % todoList[index]["author"], index, todoList[index]["condition"].upper(), todoList[index]["text"])

    def _walkthrough(path):
        if os.path.isdir(path):
            for filename in os.listdir(path):
                if filename[0] != ".":
                    for item in _walkthrough(os.path.join(path, filename)):
                        yield item
        else:
            yield path

    def _linecount(string, linenum):
        for char in string:
            if char == "\n":
                linenum += 1
        return linenum

    def _availableCommands():
        print "Commands available:\033[1m"
        print "   ",
        allObjects = copy.copy(globals())
        allKeys = allObjects.keys()
        allKeys.sort()
        def function():
            pass
        count = 0
        for objectName in allKeys:
            if objectName[0] != "_" and type(allObjects[objectName]) == type(function):
                # TODO: Print the command names in grids
                print objectName + " " * (8 - len(objectName)),
                count += 1
                if count % 5 == 0:
                    print
                    print "   ",
        if count % 5 != 0:
            print
        print "\033[m"


    def init(*args):
        """Command \033[1mINIT\033[m - synopsis: "\033[1mtodo init\033[m"
    Use this command to initialize an empty todo list in a directory."""
        todoDir = os.path.join(os.getcwd(), ".todo")
        if os.path.isdir(todoDir):
            os.system("rm -r -f %s" % todoDir)
        os.mkdir(todoDir)
        os.chmod(todoDir, 0777)
        print "Initialized!"

    def add(*args):
        """Command \033[1mADD\033[m - synopsis: "\033[1mtodo add <message> [<detail>]\033[m"
    Use this command to add a new todo item in current todo list.

PARAMETERS:
    \033[4m<message>\033[m: The message you want to show for your todo item.
     \033[4m<detail>\033[m: (optional) The detail of this todo item, which can be read using \033[1mtodo detail\033[m."""
        if len(args) > 0:
            if len(args) > 1:
                detail = args[1]
            else:
                detail = ""
            todoList = _todoList()
            _addLine(todoList, args[0], detail)
            _saveTodoList(todoList)
            print "Line added:"
            print _line(todoList, len(todoList) - 1)
        else:
            print "What do you want me to add? Use \"\033[1mtodo add <message> [<detail>]\033[m\"."

    def edit(*args):
        """Command \033[1mEDIT\033[m - synopsis: "\033[1mtodo edit <id> <message> [<detail>]\033[m"
    Use this command to edit the message and the detail of an todo item.

PARAMETERS:
         \033[4m<id>\033[m: A int number that specifies the todo item you want to edit, which can be get using \033[1mtodo show\033[m.
    \033[4m<message>\033[m: The new message you want to show for your todo item.
     \033[4m<detail>\033[m: (optional) The new detail of this todo item. If this is not set, then the todo item will keep the old detail."""
        if len(args) > 1:
            todoList = _todoList()
            try:
                entryId = int(args[0])
            except ValueError:
                print "Which item do you want to edit? Use \"\033[1mtodo edit <id> <message> [<detail>]\033[m\"."
            else:
                if entryId >= len(todoList) or not todoList[entryId]:
                    print "Item with id \"%d\" doesn't exist." % entryId
                else:
                    todoList[entryId]["text"] = args[1]
                    if len(args) > 2:
                        todoList[entryId]["detail"] = args[2]
                    _saveTodoList(todoList)
                    print "Line edited:"
                    print _line(todoList, entryId)
        elif len(args) == 1:
            print "What do you want to use as the new text? Use \"\033[1mtodo edit <id> <message> [<detail>]\033[m\"."
        elif len(args) == 0:
            print "Which item do you want to edit? Use \"\033[1mtodo edit <id> <message> [<detail>]\033[m\"."

    def done(*args):
        """Command \033[1mDONE\033[m - synopsis: "\033[1mtodo done <id>\033[m"
    Use this command to set a todo item as done.

PARAMETERS:
    \033[4m<id>\033[m: A int number that specifies the todo item you want to set done, which can be get using \033[1mtodo show\033[m."""
        if len(args) > 0:
            todoList = _todoList()
            try:
                entryId = int(args[0])
            except ValueError:
                print "Which item do you want to set done? Use \"\033[1mtodo done <id>\033[m\"."
            else:
                if entryId >= len(todoList) or not todoList[entryId]:
                    print "Item with id \"%d\" doesn't exist." % entryId
                elif todoList[entryId]["condition"] != "open":
                    print "Item with id \"%d\" is not open:" % entryId
                    print _line(todoList, entryId)
                else:
                    todoList[entryId]["condition"] = "done"
                    _saveTodoList(todoList)
                    print "Line condition set to \"DONE\":"
                    print _line(todoList, entryId)
        else:
            print "Which item do you want to set done? Use \"\033[1mtodo done <id>\033[m\"."

    def remove(*args):
        """Command \033[1mREMOVE\033[m - synopsis: "\033[1mtodo remove [-r] <id>\033[m"
    Use this command to remove a todo item.

PARAMETERS:
    \033[4m<id>\033[m: A int number that specifies the todo item you want to remove, which can be get using \033[1mtodo show\033[m.

OPTIONS:
      \033[4m-r\033[m: Remove a todo item completely instead of just marking it as deleted."""
        if "-r" in args:
            args = list(args)
            args.remove("-r")
            real = True
        else:
            real = False
        if len(args) > 0:
            todoList = _todoList()
            try:
                entryId = int(args[0])
            except ValueError:
                print "Which item do you want to remove? Use \"\033[1mtodo remove [-r] <id>\033[m\"."
            else:
                if entryId >= len(todoList) or not todoList[entryId]:
                    print "Item with id \"%d\" doesn't exist." % entryId
                else:
                    if real:
                        print "This is \033[1mREAL\033[m removing! (You cannot undo it)"
                        answer = raw_input("Are you sure to remove it? (y/n): ")
                        if answer.lower() != "y":
                            print "Not removing!"
                            return
                        print "Line removed (real removing):"
                        print _line(todoList, entryId)
                        todoList[entryId] = None
                        _saveTodoList(todoList)
                        grabList = _grabList()
                        if entryId in grabList:
                            grabList.remove(entryId)
                            _saveGrabList(grabList)
                    else:
                        if todoList[entryId]["condition"] == "remv":
                            print "Item with id \"%d\" is already removed:" % entryId
                            print _line(todoList, entryId)
                        else:
                            todoList[entryId]["condition"] = "remv"
                            todoList[entryId]["exported"] = False
                            _saveTodoList(todoList)
                            print "Line removed:"
                            print _line(todoList, entryId)
        else:
            print "Which item do you want to remove? Use \"\033[1mtodo remove [-r] <id>\033[m\"."

    def reopen(*args):
        """Command \033[1mREOPEN\033[m - synopsis: "\033[1mtodo reopen <id>\033[m"
    Use this command to reopen a todo item.

PARAMETERS:
    \033[4m<id>\033[m: A int number that specifies the todo item you want to reopen, which can be get using \033[1mtodo show\033[m."""
        if len(args) > 0:
            todoList = _todoList()
            try:
                entryId = int(args[0])
            except ValueError:
                print "Which item do you want to reopen? Use \"\033[1mtodo reopen <id>\033[m\"."
            else:
                if entryId >= len(todoList) or not todoList[entryId]:
                    print "Item with id \"%d\" doesn't exist." % entryId
                elif todoList[entryId]["condition"] == "open":
                    print "Item with id \"%d\" is already open:" % entryId
                    print _line(todoList, entryId)
                else:
                    todoList[entryId]["condition"] = "open"
                    todoList[entryId]["exported"] = False
                    _saveTodoList(todoList)
                    print "Line reopened:"
                    print _line(todoList, entryId)
        else:
            print "Which item do you want to reopen? Use \"\033[1mtodo reopen <id>\033[m\"."

    def show(*args):
        """Command \033[1mSHOW\033[m - synopsis: "\033[1mtodo show [-a|-d|-r]\033[m"
    Use this command to show the todo items. Default range is opened items, use options to change ranges.

OPTIONS:
    \033[4m-a\033[m: Show todo items of all conditions.
    \033[4m-d\033[m: Show todo items that are done.
    \033[4m-r\033[m: Show todo items that are marked as removed."""
        condition = "open"
        allcondition = False
        if "-a" in args:
            allcondition = True
        elif "-d" in args:
            condition = "done"
        elif "-r" in args:
            condition = "remv"
        todoList = _todoList()
        output = ""
        count = 0
        for index in xrange(len(todoList)):
            if todoList[index] and (allcondition or todoList[index]["condition"] == condition):
                output += _line(todoList, index) + "\n"
                count += 1
        if allcondition:
            if output:
                print "Displayed all items (%d)\n%s" % (count, output[:-1])
            else:
                print "Nothing to display!"          
        else:
            if output:
                print "Displayed condition: %s (%d)\n%s" % (condition.upper(), count, output[:-1])
            else:
                print "Nothing to display on condition \"%s\"!" % condition.upper()

    def detail(*args):
        """Command \033[1mDETAIL\033[m - synopsis: "\033[1mtodo detail <id>\033[m"
    Use this command to show the detail of a todo item.
    
PARAMETERS:
    \033[4m<id>\033[m: A int number that specifies the todo item of which you want to see the detail, which can be get using \033[1mtodo show\033[m."""
        if len(args) > 0:
            todoList = _todoList()
            try:
                entryId = int(args[0])
            except ValueError:
                print "Which item do you want to see? Use \"todo detail <id>\"."
            else:
                if entryId >= len(todoList) or not todoList[entryId]:
                    print "Item with id \"%d\" doesn't exist." % entryId
                else:
                    print _line(todoList, entryId)
                    print "Time: %s" % todoList[entryId]["time"]
                    print "Detail:"
                    print todoList[entryId]["detail"]
        else:
            print "Which item do you want to see? Use \"todo detail <id>\"."
        

    def export(*args):
        """Command \033[1mEXPORT\033[m - synopsis: "\033[1mtodo export [<message>]\033[m"
    Use this command to make a list of recently done items, so that you can use it as a commit description of version control systems. Every item will only be exported once and will not appear when you export next time.

PARAMETERS:
    \033[4m<message>\033[m: (optional) The message that you want to put before the list. If not a message is passed, then there will be no line before the list."""
        if len(args) > 0:
            print "%s\n" % args[0]
        todoList = _todoList()
        output = ""
        count = 0
        for index in xrange(len(todoList)):
            if todoList[index] and todoList[index]["condition"] == "done" and not todoList[index]["exported"]:
                todoList[index]["exported"] = True
                output += _line(todoList, index) + "\n"
                count += 1
        _saveTodoList(todoList)
        if count:
            print "TODO item done in this commit (exported by TODO in Python):\n%s" % output[:-1]
        else:
            print "No TODO item done in this commit."

    def preview(*args):
        """Command \033[1mEXPORT\033[m - synopsis: "\033[1mtodo export [<message>]\033[m"
    Use this command to preview the list of recently done items, so that you can use it as a commit description of version control systems. You can look through the items you have done using this command without worrying them being marked as exported.

PARAMETERS:
    \033[4m<message>\033[m: (optional) The message that you want to put before the list. If not a message is passed, then there will be no line before the list."""
        print "Just previewing:"
        print
        if len(args) > 0:
            print "%s\n" % args[0]
        todoList = _todoList()
        output = ""
        count = 0
        for index in xrange(len(todoList)):
            if todoList[index] and todoList[index]["condition"] == "done" and not todoList[index]["exported"]:
                output += _line(todoList, index) + "\n"
                count += 1
        if count:
            print "TODO item done in this commit (exported by TODO in Python):\n%s" % output[:-1]
        else:
            print "No TODO item done in this commit."

    def grab(*args):
        """Command \033[1mGRAB\033[m - synopsis: "\033[1mtodo grab\033[m"
    Use this command to grab all todo items in your code, which should be in comments and start with "\033[1mTODO:\033[m". It will not grab the same todo for several times even if you run it for multiple times."""
        todoList = _todoList()
        grabList = _grabList()
        for index in grabList:
            if todoList[index]["condition"] == "open":
                todoList[index]["condition"] = "done"
        for path in _walkthrough(os.getcwd()):
            relpath = os.path.relpath(path)
            extension = os.path.splitext(path)[1][1:]
            # TODO: Add more extension types
            # TODO: Use better way to determine language than extension
            if extension in ("c", "cpp", "h", "m"):
                # C, C++, Obj-c
                sign = {"//": "\n", "/*": "*/"}
            elif extension == "pas":
                # Pascal
                sign = {"{": "}"}
            elif extension == "py":
                # Python
                sign = {"#": "\n"}
            else:
                continue
            print "Scanning %s" % relpath
            allsign = copy.copy(sign)
            allsign.update({'"': '"', "'": "'"}) # TODO: For python add triple quote analysis
            strings = list()
            linenum = 1
            f = open(path)
            text = f.read()
            f.close()
            while True:
                location = len(text)
                start = ""
                for item in allsign:
                    pos = text.find(item)
                    if pos >= 0 and pos < location:
                        location = pos
                        start = item
                if len(start) == 0:
                    break
                linenum = _linecount(text[:location + len(start)], linenum)
                text = text[location + len(start):]
                pos = text.find(allsign[start])
                if pos < 0:
                    pos = len(text)
                sub = text[:pos]
                if start in sign:
                    subs = [line.strip() for line in sub.split("\n")]
                    for index in xrange(len(subs)):
                        line = subs[index]
                        if line.upper().startswith("TODO:"):
                            strings.append((linenum + index, line[5:].strip()))
                linenum = _linecount(text[:pos + len(allsign[start])], linenum)
                text = text[pos + len(allsign[start]):]
            for item in strings:
                print "    Found: (line %03d) %s" % item
                found = False
                for index in grabList:
                    # TODO: Better way to identify previous grabbing results
                    if todoList[index]["path"] == relpath and todoList[index]["text"] == item[1] and todoList[index]["condition"] == "done":
                        todoList[index]["detail"] = "TODO grabbed from %s, line %d." % (relpath, item[0])
                        todoList[index]["condition"] = "open"
                        found = True
                        break
                if not found:
                    _addLine(todoList, "%s" % item[1], "TODO grabbed from %s, line %d." % (relpath, item[0]), "TODO grabber", {"path": relpath})
                    grabList.append(len(todoList) - 1)
        _saveGrabList(grabList)
        _saveTodoList(todoList)


    # Main program
    if len(sys.argv) < 3:
        print
        print "Command name not found!"
        print
        _availableCommands()
    else:
        if sys.argv[1] in ("--help", "-h"):
            print
            print "Todo is a todo list written in Python. It allows you to grab all your todo items in your src files and read them together."
            print
            _availableCommands()
        else:
            try:
                func = eval(sys.argv[1])
            except NameError:
                print "Unknown command name \"%s\"!" % sys.argv[1]
            else:
                if len(sys.argv) > 3 and sys.argv[2] in ("--help", "-h"):
                    print
                    if func.func_doc:
                        print func.func_doc
                    else:
                        print "Command \"%s\" does not have help!" % sys.argv[1]
                    print
                else:
                    if sys.argv[1] != "export":
                        print
                    func(*sys.argv[2:-1])
                    if sys.argv[1] != "export":
                        print

del magic
