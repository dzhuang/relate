#! /bin/sh

USER=www-data
RELATE_GIT_ROOT=/srv/www/relate/course-git

for i in "$RELATE_GIT_ROOT"/*; do
  echo $i
  if test -d "$i/.git"; then
    su $USER -c "cd $i ; git repack -a -d"
  fi
done

