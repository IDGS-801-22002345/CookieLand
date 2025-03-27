# Comando para poder usar tw

npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch

# Hacer push de los cambios

git add .

git commit -m "Comentario que quieran identificar este commmit, de preferencia que es lo que hicieron"

# Antes de hacer push, verificar si no hay cambios en el main

git checkout main

git pull

# Regresan a su rama donde estaban trabajando

git checkout nombre_de_su_rama

git merge main

# Si hay conflictos tienen que solucionarlo, si solo hubo cambios pero no conflictos pues solo siguen los pasos siguientes:

git add .

git commit -m "merge con main"

git push

## En caso de no les salio ningun problema y se hizo bien el push, van hacer el PR en la pagina de git y me avisan por el grupo de whast (Dudas o comentarios me dicen)
