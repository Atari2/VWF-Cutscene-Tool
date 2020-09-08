import sys
import re

def define(definitions):
    def_path = definitions
    try:
        with open(def_path, "r") as f:
            content = f.read()
            f.close()
    except:
        print ("couldn't open "+def_path+" for reading.")
        quit()
    
    content = re.sub(r"\s+", r"", content)

    result = []
    i = 0
    while i < 0x51:
        tag = re.search(r"^(\[[^\[\]]+?\])", content)
        tag2 = re.search(r"^([^\[\]])", content)
        if tag:
            content = re.sub(r"^(\[[^\[\]]+?\])", r"", content)
            current_def = tag.group()
            result = get_tag(current_def)
            if current_def in result:
                print ("Your tag: "+str(current_def)+" is duplicated with the reserved tag.")
                quit()
            else:
                definition[current_def] = i
        elif tag2:
            content = re.sub(r"^([^\[\]])", r"", content)
            current_def = tag2.group()
            definition[current_def] = i
        else:
            print ("Invalid tag")
            quit()

        i = i+1

    print ("Finished defining\n")


def convert(convert_path):
    try:
        with open(convert_path, "r") as f:
            content = f.readlines()
    except:
        print ("couldn't open "+convert_path+" for reading.")
        quit()


    for x in range(len(content)):
        line = content[x]
        line_ = re.sub(r"\/\/.*", r"", line)
        line_ = re.sub(r"^\s+|\s+$", r"", line_)
        if line == None:
            continue
        current_file = re.search(r"^([0-9A-Fa-f]+)\s+(.+)$", line_)
        if current_file.group():
            convert_txt(current_file.group(1), current_file.group(2))
        else:
            print ("Line "+str(x)+": Invalid information, "+line_)

def convert_txt(msg_number, msg_path):
    try:
        msg_num = int(msg_number, 16)
    except:
        print ("Number isn't a valid number!")
        quit()
    
    if msg_num >= 0x100:
        print ("The specified number is too high: "+str(msg_number))

    try:
        with open("msg/"+msg_path, "r") as f:
            content = f.read()
    except:
        print ("couldn't open "+msg_path+" for reading.")
        quit()

    content = re.sub(r"\/\/.*", r"", content)       # comments
    content = re.sub(r"^\s+|\s+$", r"", content)    # leading or ending spaces
    content = re.sub(r"[\r\t\f]+", r"", content)   # line breaks

    original_content = content

    global bin_data, cur_num, num_used
    data = []
    data_2 = []
    labels = {}
    string = ""
    command = []
    for pass_ in range(2):
        data = []
        space = [-1]
        topic = 0
        content = original_content
        p = 0
        while content:
            parse_tag = re.search(r"^(\[[^\[\]]+?\])", content)
            parse_space = re.search(r"^\s+", content)
            parse_tag2 = re.search(r"^([^\[\]])", content)
            if parse_tag:
                content = re.sub(r"^(\[[^\[\]]+?\])", r"",content)
                string = parse_tag.group()
                p = p+1
            elif parse_space:
                content = re.sub(r"^\s+", r"",content)
                if space[0] >= 0:
                    space[0] = 1
                continue
            elif parse_tag2:
                content = re.sub(r"^([^\[\]])", r"",content)
                string = parse_tag2.group()
                p = p+1
            else: 
                print ("Invalid tag found. It may be the tag is unclosed or it contains nothing")
                quit()

            j = 1
            try:
                get_def = definition[string]
            except:
                j = 0
            command = get_tag(string)

            if j == 1:
                if space[0] > 0:
                    data.append(0x81)
                    data_2.append("[ ]")
                data.append(get_def)
                data_2.append(string)
                space[0] = 0

            elif command[0]:
                if command[0] & 0x80:               # ?
                    data.append(command[0])                
                    data_2.append(command[1])
                
                if command[0] == 0x01:              # label
                    labels[command[2]] = len(data) + 1
                    data_2.append(command[1])
                    data_2.append(command[2])

                elif command[0] == 0x80:            # end
                    space[0] = -1
                    parse_command_1 = re.search(r"^exit$", command[2])
                    parse_command_2 = re.search(r"^goal$", command[2])
                    parse_command_3 = re.search(r"^sgoal$", command[2])
                    data_2.append(command[2])
                    if parse_command_1:
                        data.append(0x20)
                    elif parse_command_2:
                        data.append(0x21)
                    elif parse_command_3:
                        data.append(0x22)
                    else:
                        cur_data = int(command[2],16)
                        if cur_data < 0x20:
                            data.append(cur_data)
                        else:
                            print("The specified number in [end=*] is too high.")
                            quit()

                elif command[0] == 0x82:                # line break
                    space[0] = -1

                elif command[0] == 0x84:                # wait timer
                    cur_data = int(command[2])
                    if cur_data < 0x100:
                        data.append(cur_data)
                        data_2.append(command[2])
                    else:
                        print ("The specified number in [wait=*] is too high.")
                        quit()

                elif command[0] == 0x88:                # pad left
                    cur_data = int(command[2])
                    if cur_data < 0x100:
                        data.append(cur_data)
                        data_2.append(command[2])
                    else:
                        print ("The specified number in [pad left=*] is too high.")
                        quit()

                elif command[0] == 0x89:                # pad right
                    cur_data = int(command[2])
                    if cur_data < 0x100:
                        data.append(cur_data)
                        data_2.append(command[2])
                    else:
                        print ("The specified number in [pad right=*] is too high.")
                        quit()

                elif command[0] == 0x8A:                # pad
                    cur_data_1 = int(command[2])
                    cur_data_2 = int(command[3])
                    data_2.append(command[2])
                    data_2.append(command[3])
                    if cur_data < 0x100 and cur_data < 0x100:
                        data.append(cur_data_1)
                        data.append(cur_data_2)
                    else:
                        print ("The specified number in [pad=*,*] is too high.")
                        quit()
                    
                elif command[0] == 0x8B:                # music
                    cur_data = int(command[2])
                    if cur_data < 0x100:
                        data.append(cur_data)
                    else:
                        print ("The specified number in [music=*] is too high.")
                        quit()
                    
                elif command[0] == 0x8C:                # erase
                    space[0] = -1
                    
                elif command[0] == 0x8D:                # topic
                    topic = (topic + 1) & 1
                    if topic:
                        space.insert(0, -1)
                    else:
                        space.pop(0)

                elif command[0] == 0x8E:                # sprite
                    loop = int(command[2])
                    data_2.append(command[2])
                    if loop == 0 or loop >= 0x7F:
                        print ("The specified number in [sprite=*] is not in the range 1-7F.")
                        quit()
                    data.append(loop)
                    sprite_data = re.search(r"^\s*((?:.|\s)*?)\s*\[\s*\/sprite\s*\]", content)
                    content = re.sub(r"^\s*((?:.|\s)*?)\s*\[\s*\/sprite\s*\]", r"", content)
                    if sprite_data:
                        sprite = sprite_data.group(1)
                        sprite = re.sub(r"\s+", r"", sprite)
                        while sprite:
                            sprite_tile = re.search(r"^\(([0-9A-Fa-f]+),([0-9A-Fa-f]+),([0-9A-Fa-f]+),([0-9A-Fa-f]+),(big|small)\)", sprite)
                            sprite = re.sub(r"^\(([0-9A-Fa-f]+),([0-9A-Fa-f]+),([0-9A-Fa-f]+),([0-9A-Fa-f]+),(big|small)\)", r"", sprite)
                            
                            if sprite_tile:
                                data.append(int(sprite_tile.group(1), 16))
                                data.append(int(sprite_tile.group(2), 16))
                                data.append(int(sprite_tile.group(3), 16))
                                if "big" in sprite_tile.group(5):
                                    data.append((int(sprite_tile.group(4), 16) & 0xCF) | 0x20)
                                else:
                                    data.append((int(sprite_tile.group(4), 16) & 0xCF))
                                data_2.append(sprite_tile.group(1))
                                data_2.append(sprite_tile.group(2))
                                data_2.append(sprite_tile.group(3))
                                data_2.append(sprite_tile.group(4)+" "+sprite_tile.group(5))
                                loop = loop-1
                            else:
                                print ("Invalid attributes in [sprite=*,*][/sprite]")
                        if loop:
                            print ("The number of attributes in [sprite=*,*][/sprite] not matched to the loop number")
                            quit()
                    else: 
                        print ("Unclosed [sprite] tag found.")
                        quit()


                elif command[0] == 0x90:
                    space[0] = -1
                    branches = command[2].split(",")
                    data_2.append(command[2])
                    nums = len(branches)
                    if nums < 2 or 5 < nums:
                        print ("The number of labels in [branch=*] is either too high or too small.")
                        quit()
                    if pass_ == 0:
                        data.append(0x00)
                        data_2.append(command[1])
                        for k in range(nums):
                            data.append(0x00)
                            data.append(0x00)
                    else:
                        branch_data = re.search(r"^\[\s*branch2", command[1])
                        if branch_data:
                            data.append(nums|0x80)
                        else:
                            data.append(nums)
                        for x in range(len(branches)):
                            branch_search = re.search(r"^\s+|\s+$", command[1])
                            branch_data = re.sub(r"^\s+|\s+$", r"", command[1])
                            if branch_data:
                                pass
                            else:
                                print ("The empty label is specified in [branch=*].")
                                quit()

                            try:
                                branch_data_ = labels[branches[x]]
                                data.append(branch_data_ & 0xFF)
                                data.append(branch_data_ >> 8)
                            except:
                                print ("The label in [branch=*] not defined yet.")
                                quit()

                elif command[0] == 0x91:                # jump
                    space[0] = -1
                    if pass_ == 0:
                        data.append(0x00)
                        data.append(0x00)
                        data_2.append(command[1])
                        data_2.append(command[2])
                    else:
                        try:
                            jump_data = labels[command[2]]
                            data.append(jump_data & 0xFF)
                            data.append(jump_data >> 8)
                            data_2.append(command[1])
                            data_2.append(command[2])
                        except:
                            print ("The label in [jump=*] not defined yet.")
                            quit()

                elif command[0] == 0x92:                # skip
                    if pass_ == 0:
                        data.append(0x00)
                        data.append(0x00)
                        data_2.append(command[1])
                        data_2.append(command[2])
                    else:
                        try:
                            skip_data = labels[command[2]]
                            data.append(skip_data & 0xFF)
                            data.append(skip_data >> 8)
                            data_2.append(command[1])
                            data_2.append(command[2])
                        except:
                            print ("The label in [skip=*] not defined yet.")
                            quit()

    cur_num = cur_num+1
    num_used[msg_number] = cur_num
    bin_data.append(data)
    print ("'"+msg_path+"' conversion finished. Total size: 0x{:02X} bytes".format(len(data)+1))

    with open("parsed.txt", "w") as f:
        for x in range(len(data)):
            index = "{0:04X}".format(x)
            data_ = "{0:02X}".format(int(data[x]))
            f.write("$"+index+": (0x"+data_+") "+data_2[x]+"\n")
        f.close()
            

def error(parse_error, orig_content, content):
    pass


def create(output_path):
    global num_used, bin_data
    print ("Creating txt...")
    with open(output_path, "w") as f:
        vwf_data = ""
        ptr = "DataPtr:"
        for i in range(len(num_used.keys())):
            if (i & 15) == 0:
                ptr = ptr + "\n\t\t\tdw"
            else: 
                ptr = ptr + ", "
            try:
                get_num = num_used["{:02d}".format(i)]-1
                ptr = ptr+" .{:02X}".format(i)
                vwf_data = vwf_data+"\n.{:02X}".format(i)
                j = 0
                for j in range(len(bin_data[get_num])):
                    if (j & 0x1F) == 0:
                        vwf_data = vwf_data + "\n\t\t\tdb " + "${:02X}".format(bin_data[get_num][j] & 0xFF)
                    else:
                        vwf_data = vwf_data + "," + "${:02X}".format(bin_data[get_num][j] & 0xFF)
                del num_used["{:02d}".format(i)]
            except:
                pass
        

        code = """
incsrc "vwf_defines.asm"

print "INIT ",pc
	PHX
	PHK
	PLA
	STA.l !VWF_DATA+$02
	REP #$30
	LDA !E4,x
	AND #$00F0
	LSR #3
	STA $00
	LDA !D8,x
	AND #$00F0
	ASL 
	ORA $00
	TAX
	LDA.l DataPtr,x
	STA.l !VWF_DATA
	SEP #$30
	PLX

print "MAIN ",pc
	RTL

"""

        f.write(code+"\n"+ptr+"\n"+vwf_data)

            
def get_tag(orig_tag):
    r = re.search(r"^\[\s*end\s*=\s*([0-9A-Fa-f]+|exit|s?goal)\s*\]",orig_tag)
    if r: 
        result = [0x80, r.group(),r.group(1)]
        return result
    r = re.search(r"^\[ \]", orig_tag)
    if r: 
        result = [0x81, r.group()]
        return result
    r = re.search(r"^\[\s*br\s*\]", orig_tag)
    if r: 
        result = [0x82, r.group()]
        return result
    r = re.search(r"^\[\s*wait\s*\]", orig_tag)
    if r: 
        result = [0x83, r.group()]
        return result
    r = re.search(r"^\[\s*wait\s*=\s*(\d+)\s*\]", orig_tag)
    if r: 
        result = [0x84, r.group(), r.group(1)]
        return result
    r = re.search(r"^\[\s*(?:font\s+colou?r\s*=\s*1|\/font\s+colou?r)\s*\]", orig_tag)
    if r: 
        result = [0x85, r.group()]
        return result
    r = re.search(r"^\[\s*font\s+colou?r\s*=\s*2\s*\]", orig_tag)
    if r: 
        result = [0x86, r.group()]
        return result
    r = re.search(r"^\[\s*font\s+colou?r\s*=\s*3\s*\]", orig_tag)
    if r: 
        result = [0x87, r.group()]
        return result
    r = re.search(r"^\[\s*pad\s+left\s*=\s*(\d+)\s*\]", orig_tag)
    if r: 
        result = [0x88, r.group(), r.group(1)]
        return result
    r = re.search(r"^\[\s*pad\s+right\s*=\s*(\d+)\s*\]", orig_tag)
    if r: 
        result = [0x89, r.group(), r.group(1)]
        return result
    r = re.search(r"^\[\s*pad\s*=\s*(\d+)\s*,\s*(\d+)\s*\]", orig_tag)
    if r: 
        result = [0x8A, r.group(), r.group(1), r.group(2)]
        return result
    r = re.search(r"^\[\s*music\s*=\s*([0-9a-fA-F]+)\s*\]", orig_tag)
    if r: 
        result = [0x8B, r.group(), r.group(1)]
        return result
    r = re.search(r"^\[\s*erase\s*\]", orig_tag)
    if r: 
        result = [0x8C, r.group()]
        return result
    r = re.search(r"^\[\s*\/?topic\s*\]", orig_tag)
    if r: 
        result = [0x8D, r.group()]
        return result
    r = re.search(r"^\[\s*sprite\s*=\s*([0-9A-Fa-f]+)\s*\]", orig_tag)
    if r: 
        result = [0x8E, r.group(), r.group(1)]
        return result
    r = re.search(r"^\[\s*sprite\s*=\s*erase\s*\]", orig_tag)
    if r: 
        result = [0x8F, r.group()]
        return result
    r = re.search(r"^\[\s*branch2?\s*=\s*(.+)\s*\]", orig_tag)
    if r: 
        result = [0x90, r.group(), r.group(1)]
        return result
    r = re.search(r"^\[\s*jump\s*=\s*(.+)\s*\]", orig_tag)
    if r: 
        result = [0x91, r.group(), r.group(1)]
        return result
    r = re.search(r"^\[\s*skip\s*=\s*(.+)\s*\]", orig_tag)
    if r: 
        result = [0x92, r.group(), r.group(1)]
        return result
    r = re.search(r"^\[\s*\/\s*skip\s*\]", orig_tag)
    if r: 
        result = [0x93, r.group()]
        return result
    r = re.search(r"^\[\s*label\s*=\s*(.+)\s*\]", orig_tag)
    if r: 
        result = [0x01, r.group(), r.group(1)]
        return result

    result = [0x00]
    return result



if len(sys.argv) < 3:
    print ("Usage: definition.txt list.txt output.txt")
    quit()

bin_data = []
num_used = {}
cur_num = 0
definition = {}
org_content = 0
content = 0

define(sys.argv[1])
convert(sys.argv[2])
create(sys.argv[3])