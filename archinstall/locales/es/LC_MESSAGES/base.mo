��    M      �  g   �      �  L   �  i   �     @     _  $   y  <   �     �     �  ;     #   B  #   f     �  .   �     �  '   �     	  1   )	  3   [	  :   �	  L   �	  B   
  :   Z
  @   �
  w   �
  v   N  i   �  �   /  e   �  v   #     �     �     �     �     �               *     <     K     b     y     �  )   �  3   �  &     3   *  )   ^     �  J   �  :   �  D   (  6   m  H   �     �          #  )   5     _     o     �  p   �  Q        a  6   j  G   �  C   �  Z   -  #   �  M   �  2   �  .   -  .   \  /   �  1   �  1   �  D     �   d  r   .  n   �       "   0  $   S  Q   x     �     �  G     #   I     m     �  5   �  '   �  '   �     "  C   ;  E     :   �  T      O   U  U   �  U   �  �   Q  �   �  k   b  �   �  a   n  s   �      D  #   e  '   �     �     �  "   �  )        .     J  '   a  !   �     �      �  .   �  6      /   M   9   }   )   �      �   R   �   J   Q!  [   �!  G   �!  V   @"  7   �"  $   �"  !   �"  3   #     J#  %   `#      �#  {   �#  U   #$  	   y$  =   �$  Z   �$  H   %  o   e%     �%  a   �%  B   W&  5   �&  3   �&  5   '  5   :'  D   p'  S   �'             *                 8      -         D   M   >                           "                              	   <   :   
       ,   K          ;   =   I   #   L   @   &                  G   5   /   A   H                    3   %                      .   E      $   7   ?      +   C          9            '   0   (      4         )   6   B   2   J   1          !   F              

Select a graphics driver or leave blank to install all open-source drivers  * Partition mount-points are relative to inside the installation, the boot would be /boot as an example. Additional packages to install All open-source (default) And one more time for verification:  Any additional users to install (leave blank for no users):  Choose a bootloader Choose an audio server Choose which kernels to use or leave blank for default "{}" Choose which locale encoding to use Choose which locale language to use Configure network Copy ISO network configuration to installation Current partition layout Desired hostname for the installation:  Do you really want to abort? Enter a desired filesystem type for the partition Enter a desired filesystem type for the partition:  Enter the IP and subnet for {} (example: 192.168.0.5/24):  Enter the end sector of the partition (percentage or block number, ex: {}):  Enter the start sector (percentage or block number, default: {}):  Enter your DNS servers (space separated, blank for none):  Enter your gateway (router) IP address or leave blank for none:  For the best compatibility with your AMD hardware, you may want to use either the all open-source or AMD / ATI options. For the best compatibility with your Intel hardware, you may want to use either the all open-source or Intel options.
 For the best compatibility with your Nvidia hardware, you may want to use the Nvidia proprietary driver.
 Hardware time and other post-configuration steps might be required in order for NTP to work.
For more information, please check the Arch wiki If you desire a web browser, such as firefox or chromium, you may specify it in the following prompt. Only packages such as base, base-devel, linux, linux-firmware, efibootmgr and optional profile packages are installed. Password for user "{}":  Select Archinstall language Select Keyboard layout Select a timezone Select audio Select bootloader Select disk layout Select harddrives Select kernels Select keyboard layout Select locale encoding Select locale language Select mirror region Select one network interface to configure Select one of the regions to download packages from Select one of the values shown below:  Select one or more hard drives to use and configure Select one or more of the options below:  Select what to do with
{} Select what to do with each individual drive (followed by partition usage) Select what you wish to do with the selected block devices Select where to mount partition (leave blank to remove mountpoint):  Select which filesystem your main partition should use Select which mode to configure for "{}" or skip to use default mode "{}" Set automatic time sync (NTP) Set encryption password Set root password Should this user be a superuser (sudoer)? Specify profile Specify superuser account Specify user account This is a list of pre-programmed profiles, they might make it easier to install things like desktop environments Use NetworkManager (necessary to configure internet graphically in GNOME and KDE) Use swap Username for required superuser with sudo privileges:  Wipe all selected drives and use a best-effort default partition layout Would you like to use GRUB as a bootloader instead of systemd-boot? Would you like to use automatic time synchronization (NTP) with the default time servers?
 Would you like to use swap on zram? Write additional packages to install (space separated, leave blank to skip):  {}

Select by index which partition to mount where {}

Select by index which partitions to delete {}

Select which partition to mark as bootable {}

Select which partition to mark as encrypted {}

Select which partition to mask for formatting {}

Select which partition to set a filesystem on {} contains queued partitions, this will remove those, are you sure? Project-Id-Version: 
PO-Revision-Date: 
Last-Translator: 
Language-Team: 
Language: de
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
X-Generator: Poedit 3.0
 

Selecciona un controlador de gráficos o deja en blanco para instalar todos los controladores de código abierto  * Los puntos de montaje de partición son relativos a la instalación, el arranque sería /boot como ejemplo. Paquetes adicionales a instalar Todo código abierto (por defecto) Una última vez para verificación:  Algún usuario adicional para instalar (deja en blanco para no agregar ninguno):  Elige un gestor de arranque Elige un servidor de audio Elige qué kernels usar o deja en blanco para usar los por defecto "{}" Elige qué codificación local usar Elige qué idioma local usar Configurar la red Copiar la configuración de red ISO a la instalación Distribución actual de las particiones Hostname deseado para la instalación:  Realmente desea abortar? Escriba el tipo de sistema de archivos que desea para la partición Escriba el tipo de sistema de archivos que desea para la partición:  Escriba la IP y subred para {} (ejemplo: 192.168.0.5/24):  Escriba el sector final de la partición (porcentaje o número de bloque, ej: {}): " Escriba el sector de inicio (porcentaje o número de bloque, por defecto: {}):  Escriba los servidores DNS (separados por espacios, en blanco para no usar ninguno):  Escriba la IP de su puerta de enlace (router) o deje en blanco para no usar ninguna:  Para la mejor compatibilidad con tu hardware AMD, puedes querer usar tanto la opción de todo código abierto como la opción AMD / ATI. Para la mejor compatibilidad con tu hardware Intel, puedes querer usar tanto la opción de todo código abierto como la opción Intel.
 Para la mejor compatibilidad con tu hardware Nvidia, puedes querer usar el controlador propietario Nvidia.
 La hora del hardware y otros pasos post-configuración pueden ser necesarios para que NTP funcione. Para más información, por favor, consulte la wiki de Arch Si desea un navegador web, como firefox o chromium, puede especificarlo en el siguiente diálogo. Solo paquetes como base, base-devel, linux, linux-firmware, efibootmgr y paquetes opcionales de perfil se instalan. Contraseña para el usuario "{}" Selecciona el idioma de Archinstall Selecciona la distribución del teclado Selecciona una zona horaria Selecciona el audio Selecciona el cargador de arranque Selecciona la distribución de los discos Selecciona los discos duros Selecciona los kernels Selecciona la distribución del teclado Selecciona la codificación local Selecciona el idioma local Selecciona la región del mirror Selecciona una interfaz de red para configurar Selecciona una de las regiones para descargar paquetes Selecciona uno de los valores mostrados abajo:  Selecciona uno o más discos duros para usar y configurar Selecciona una o más opciones de abajo:  Selecciona qué hacer con
{} Selecciona qué hacer con cada disco individual (seguido por el uso de partición) Selecciona qué quieres hacer con los dispositivos de bloque seleccionados Selecciona dónde montar la partición (deja en blanco para eliminar el punto de montaje):  Selecciona el sistema de archivos que su partición principal debe usar Selecciona el modo para configurar "{}" u omitir para usar el modo "{}" predeterminado Establecer la sincronización automática de hora (NTP) Establecer la contraseña de cifrado Establecer la contraseña de root Debería este usuario ser un superusuario (sudoer)? Especificar el perfil Especificar la cuenta de superusuario Especificar la cuenta de usuario Esta es una lista de perfiles pre-programados, pueden facilitar la instalación de aplicaciones como entornos de escritorio Usar NetworkManager (necesario para configurar internet gráficamente en GNOME y KDE) Usar swap Nombre de usuario para el superusuario con privilegios sudo:  Limpiar todos los discos seleccionados y usar una distribución de particiones por defecto Te gustaría usar GRUB como gestor de arranque en lugar de systemd-boot? Te gustaría utilizar la sincronización automática de hora (NTP) con los servidores de hora predeterminados?
 Te gustaría usar swap en zram? Escriba paquetes adicionales para instalar (separados por espacios, deja en blanco para omitir):  {}

Selecciona por índice la ubicación de la partición a montar {}

Selecciona por índice las particiones a eliminar {}

Selecciona la partición a marcar como bootable {}

Selecciona la partición a marcar como encriptada {}

Selecciona la partición a ocultar para formatear {}

Selecciona la partición a configurar con un sistema de archivos {} contiene particiones en cola, esto eliminará esas particiones, ¿estás seguro? 