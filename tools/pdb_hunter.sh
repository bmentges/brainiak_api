#! /bin/bash

[ -z "$1" ] && echo "Usage: $0 ROOT_DIRECTORY" && exit 1

ok="[$(tput setaf 2) OK $(tput sgr0)]";
failed="[$(tput setaf 1) FAILED $(tput sgr0)]";

pdbs_found="$(grep -r 'pdb' $(find $1 -type f -name '*.py' -and -not -path \*test\*) | grep -v '#')"

[ -z "$pdbs_found" ] && echo "$ok No pdb found." && exit 0

# Found some pdb
echo -n "$failed  "
echo "Some pdb calls were found:"
echo "$pdbs_found" | grep --color pdb
exit 2
