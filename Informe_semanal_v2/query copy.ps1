& C:\Users\ct_diealb\AppData\Local\anaconda3\shell\condabin\conda-hook.ps1 ; conda activate base
& C:\Users\ct_diealb\AppData\Local\anaconda3\python.exe E:\Scripts\DB_project\tools\Query_automatico_python.py
& C:\Users\ct_diealb\AppData\Local\anaconda3\shell\condabin\conda-hook.ps1 ; conda activate base
& C:\Users\ct_diealb\AppData\Local\anaconda3\python.exe E:\Scripts\DB_project\main\Planta_1_wo_graphs.py
& C:\Users\ct_diealb\AppData\Local\anaconda3\shell\condabin\conda-hook.ps1 ; conda activate base
& C:\Users\ct_diealb\AppData\Local\anaconda3\python.exe E:\Scripts\DB_project\main\Planta_2_wo_graphs.py
& C:\Users\ct_diealb\AppData\Local\anaconda3\shell\condabin\conda-hook.ps1 ; conda activate base
& C:\Users\ct_diealb\AppData\Local\anaconda3\python.exe E:\Scripts\DB_project\main\columnas.py

& Copy-Item 'E:\Scripts\DB_project\main\Ahorros\P1_Cusum.csv'  -Destination '\\10.234.40.37\c$\INFORMES_CELSIA\Datos historicos\' -Recurse -Force
& Copy-Item 'E:\Scripts\DB_project\main\Ahorros\P2_Cusum.csv'  -Destination '\\10.234.40.37\c$\INFORMES_CELSIA\Datos historicos\' -Recurse -Force
& Copy-Item 'E:\Scripts\DB_project\main\Ahorros\P1_Cusum_Ok.csv'  -Destination '\\10.234.40.37\c$\INFORMES_CELSIA\Datos historicos\' -Recurse -Force
& Copy-Item 'E:\Scripts\DB_project\main\Ahorros\P2_Cusum_Ok.csv'  -Destination '\\10.234.40.37\c$\INFORMES_CELSIA\Datos historicos\' -Recurse -Force





# Borrar los notebooks individuales por sede
& Remove-Item -Path 'C:\Users\jpocampo\Desktop\Informe_Bancolombia\CB_informes_Ubi\Informe_semanal_v2\main\notebooks\individual\*' -Recurse -Force
& C:\ProgramData\Anaconda3\python.exe C:\Users\jpocampo\Desktop\Informe_Bancolombia\CB_informes_Ubi\Informe_semanal_v2\tools\builder.ipynb
& Remove-Item 'C:\Users\jpocampo\Desktop\Informe_Bancolombia\CB_informes_Ubi\Informe_semanal_v2\main\_build' -Recurse -Force
& jb build "C:\Users\jpocampo\Desktop\Informe_Bancolombia\CB_informes_Ubi\Informe_semanal_v2\main"
