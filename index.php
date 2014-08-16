<html>
<!-- place this file in /var/www/ -->
<!-- requires php and apache to host the page on your raspberry -->

<head>
<meta charset="UTF-8" />
</head>


<?php
if (isset($_POST['gdoor']))
{
exec("sudo python /home/pi/toggle.py");
}
?>

<form method="post">
<button name="gdoor" style="font-size:64px;background-color:lightgreen;width:600;height:300">Garage Door Switch</button><br>

</form>
</html>
