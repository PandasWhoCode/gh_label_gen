import argparse
import sys

def parse_csv(csv:str) -> list[str]:
    repos:list[str] = []
    with open(csv,"r") as infile:
        for line in infile.readlines():
            repos.append(line.strip().replace(",","/"))
    return repos

def gen_topic_script(name:str, repo_list:list[str]):
    from os import chmod
    
    print("Generating the Topic Gen shell script")

    command:str = "gh repo edit [REPO] --add-topic " + name

    cmd_list:list[str] = []

    try:
        for repo in repo_list:
            cmd:str = command.replace("[REPO]",repo)
            cmd_list.append(cmd)
        
        topic_script:str = "topic_gen.sh"
        with open(topic_script,"w") as script:
            for line in cmd_list:
                line += "\n"
                print(line)
                script.write(line)
                script.write("sleep 2\n") # need sleep 2 for gh api to be happy
        
        print("Generation comlete. chmod to 755 to enable execution of the script")
        chmod(topic_script,0o755)
    
    except Exception as e:
        raise e
    
    print("Complete.")

def gen_edit_script(name:str, swap_name:str, description:str, color:str, repo_list:list[str]):
    from os import chmod
    print("Generating the Issue Edit shell script")

    command:str = "gh label edit \"" + name + "\" --repo [REPO] "
    if swap_name != "":
        command += "--name \"" + swap_name + "\" "
    if description != "":
        command += "--description \"" + description + "\" "
    if color != "":
        command += "--color \"" + color + "\" "

    cmd_list:list[str] = []

    try:
        for repo in repo_list:
            cmd:str = command.replace("[REPO]",repo)
            cmd_list.append(cmd)

        edit_script:str = "label_edit.sh"
        with open(edit_script, "w") as script:
            for line in cmd_list:
                line += "\n"
                print(line)
                script.write(line)
                script.write("sleep 2\n") # need sleep 2 for gh api to be happy

        print("Generation complete. chmod to 755 to enable execution of the script")
        chmod(edit_script,0o755)

    except Exception as e:
        raise e

    print("Complete.")

def gen_label_script(name:str, description:str, color:str, repo_list:list[str], force:bool=False):
    from os import chmod

    print("Generating the Issue Gen shell script")

    command:str = "gh label create " + name + " --repo [REPO] --description \"" + description + "\" --color \"" + color + "\""
    if force:
        command:str = "gh label create \"" + name + "\" --repo [REPO] --description \"" + description + "\" --color \"" + color + "\" --force"
    
    cmd_list:list[str] = []

    try:
        for repo in repo_list:
            cmd:str = command.replace("[REPO]",repo)
            cmd_list.append(cmd)
        
        label_script:str = "label_gen.sh"
        with open(label_script, "w") as script:
            for line in cmd_list:
                line += "\n"
                print(line)
                script.write(line)
                script.write("sleep 2\n") # need sleep 2 for gh api to be happy

        print("Generation complete. chmod to 755 to enable execution of the script")
        chmod(label_script,0o755)
    
    except Exception as e:
        raise e

    print("Complete.")

def parse_audit_args() -> tuple[str,str,str,str,str,bool,bool,bool]:
    from os.path import exists as path_exists # just need to check if os.path.exists() returns true for the audit file

    parser = argparse.ArgumentParser(description="Generate a script that will create several github labels across the repositories in the specified label_list.")
    parser.add_argument("-r","--repo-csv-file",dest="csv_file",type=str,help="The csv file which specifies all required repositories for the new label")
    parser.add_argument("-d","--description",dest="description",type=str,help="Description for the label")
    parser.add_argument("-n","--name",dest="name",type=str,help="The name for the label/topic")
    parser.add_argument("-c","--color",dest="color",type=str,help="The color code for the label (defined here: https://www.notion.so/swirldslabs/Issue-Management-db25f4d0789044d9addaa196fe10c9aa)")
    parser.add_argument("-t","--topics",dest="topics",action='store_true',help="Tell the script to generate topics instead of labels.")
    parser.add_argument("-f","--force",dest="force",action='store_true',help="Tell the script to force the push of the label if it exists.")
    parser.add_argument("-e","--edit",dest="edit",action='store_true',help="Tell the script to edit the label if it exists.")
    parser.add_argument("-s","--swap-name",dest='swap_name',type=str,help="The new name for the label when editing.")
    args = parser.parse_args()

    if args.csv_file is None or args.csv_file == "":
        raise RuntimeError("No csv_file specified")
    
    if not path_exists(args.csv_file):
        raise RuntimeError("The specified csv_file does not exist or is not valid")
    
    if args.name is None or args.name == "":
        raise RuntimeError("No label/topic name specified")
    
    if not args.topics and not args.edit and (args.color is None or args.color == ""):
        raise RuntimeError("Must specify the color for the issue (defined here: https://www.notion.so/swirldslabs/Issue-Management-db25f4d0789044d9addaa196fe10c9aa)")
    
    description:str = ""
    if args.description is not None:
        description = args.description

    swap_name:str = ""
    if args.swap_name is not None:
        swap_name = args.swap_name

    force:bool = False
    if args.force:
        force = True
    
    topics:bool = False
    if args.topics:
        topics = True

    edit:bool = False
    if args.edit:
        edit = True

    return args.csv_file, args.name, description, swap_name, args.color, force, topics, edit

def main():
    try:
        csv_name:str = ""
        name:str = ""
        description:str = ""
        swap_name:str = ""
        color:str = ""
        force:bool = False
        topics:bool = False
        edit:bool = False
        csv_name, name, description, swap_name, color, force, topics, edit = parse_audit_args()
        repo_list:list[str] = parse_csv(csv=csv_name)
        if topics:
            gen_topic_script(name=name, repo_list=repo_list)
        elif edit:
            color = "" if color is None else color
            gen_edit_script(name=name, swap_name=swap_name, description=description, color=color, repo_list=repo_list)
        else:
            gen_label_script(name=name ,description=description, color=color, repo_list=repo_list,force=force)

    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
    sys.exit(0) # clean execution exit happily
