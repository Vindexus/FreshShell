# Login banner. Sourced last so it prints after everything is set up.

printf "\e[1;37mToday is \e[34m%s \e[35m%s\e[0m\n" "$(date '+%Y-%m-%d')" "$(date '+%H:%M:%S')"
