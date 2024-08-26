import argparse
import sys

def parse_csv(csv:str) -> list[str]:
    repos:list[str] = []
    with open(csv,"r") as infile:
        for line in infile.readlines():
            repos.append(line.strip().replace(",","/"))
    return repos

def gen_label_script(name:str, description:str, color:str, repo_list:list[str], force:bool=False):
    from os import chmod

    print("Generating the Issue Gen shell script")

    command:str = "gh label create " + name + " --repo [REPO] --description \"" + description + "\" --color " + color
    if force:
        command:str = "gh label create " + name + " --repo [REPO] --description \"" + description + "\" --color " + color + " --force"
    
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

def parse_audit_args() -> tuple[str,str]:
    from os.path import exists as path_exists # just need to check if os.path.exists() returns true for the audit file

    parser = argparse.ArgumentParser(description="Generate a script that will create several github labels across the repositories in the specified label_list.")
    parser.add_argument("-r","--repo-csv-file",dest="csv_file",type=str,help="The csv file which specifies all required repositories for the new label")
    parser.add_argument("-d","--description",dest="description",type=str,help="Description for the label")
    parser.add_argument("-n","--name",dest="name",type=str,help="The name for the label")
    parser.add_argument("-c","--color",dest="color",type=str,help="The color code for the label (defined here: https://www.notion.so/swirldslabs/Issue-Management-db25f4d0789044d9addaa196fe10c9aa)")
    parser.add_argument("-f","--force",dest="force",action='store_true',help="Tell the script to force the push of the label if it exists.")
    args = parser.parse_args()

    if args.csv_file is None or args.csv_file == "":
        raise RuntimeError("No csv_file specified")
    
    if not path_exists(args.csv_file):
        raise RuntimeError("The specified csv_file does not exist or is not valid")
    
    if args.name is None or args.name == "":
        raise RuntimeError("No label name specified")
    
    if args.color is None or args.color == "":
        raise RuntimeError("Must specify the color for the issue (defined here: https://www.notion.so/swirldslabs/Issue-Management-db25f4d0789044d9addaa196fe10c9aa)")
    
    description:str = ""
    if args.description is not None:
        description = args.description

    force:bool = False
    if args.force:
        force = True

    return args.csv_file, args.name, description, args.color, force

def main():
    try:
        csv_name:str = ""
        name:str = ""
        description:str = ""
        color:str = ""
        force:bool = False
        csv_name, name, description, color, force = parse_audit_args()
        repo_list:list[str] = parse_csv(csv=csv_name)
        gen_label_script(name=name, description=description, color=color, repo_list=repo_list,force=force)

    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
    sys.exit(0) # clean execution exit happily
