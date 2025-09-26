genRepoList() {
  # check if gh is installed
  if ! command -v gh &> /dev/null; then
    echo "gh command could not be found, please install GitHub CLI."
    return 1
  fi

  # Use getopts to parse options
  # Options include target, owner, append (flag)
  local TARGET="repo_list.csv"
  local OWNER=""
  local APPEND=0
  while getopts "t:o:a" opt; do
    case ${opt} in
      t ) TARGET="$OPTARG" ;;
      o ) OWNER="$OPTARG" ;;
      a ) APPEND=1 ;;
      \? ) echo "Usage: genRepoList -t target_file -o owner [-a]"
           return 1 ;;
    esac
  done

  # Validate required parameters
  if [[ -z "$OWNER" ]]; then
    echo "Owner is required. Use -o to specify the owner."
    echo "Usage: genRepoList -o owner [-t target_file] [-a]"
    return 1
  fi

  # ensure target file exists or create it
  if [[ ! -f "$TARGET" ]]; then
    touch "$TARGET"
  fi

  # Create repo csv using gh cli
  if [[ $APPEND -eq 1 ]]; then
    gh repo list "${OWNER}" --limit 100 --json owner, name | jq -r '.[] | .owner.login + "," + .name' >> "${TARGET}"
  else
    gh repo list "${OWNER}" --limit 100 --json owner, name | jq -r '.[] | .owner.login + "," + .name' > "${TARGET}"
  fi
}

genRepoList "$@"