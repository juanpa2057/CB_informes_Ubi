# Ruta al script activate del entorno Conda
$activateScript = "C:/ProgramData/Anaconda3/Scripts/activate"

# Ejecuta el script activate para activar el entorno
& $activateScript nuevo2-env

# Ruta al archivo .ipynb que quieres ejecutar
$notebookPath = "C:\Users\jpocampo\Desktop\Informe_Bancolombia\CB_informes_Ubi\Informe_semanal_v2\tools\request.ipynb"

# Ejecuta el archivo .ipynb con jupyter nbconvert
jupyter nbconvert --to notebook --execute $notebookPath
