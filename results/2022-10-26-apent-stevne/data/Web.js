function wait(antchar,antcol) {
	calc(antchar,antcol);
	setTimeout(pageScroll,1000);
}
function pageScroll() {
		var objDiv = document.getElementById("scroll");
   	objDiv.scrollTop = objDiv.scrollTop + 1;
   	var x = parseFloat(objDiv.scrollTop);
   	var y = parseInt(getComputedStyle(document.getElementById("scroll")).height);
   	var z = parseInt(objDiv.scrollHeight);
   	if (((x + y) >= (z-2)) && (objDiv.scrollTop > 0)){
   		clearTimeout(my_time);
   		sleep(2000);
   		objDiv.scrollTop = 0;
   	}
	   	my_time = setTimeout(pageScroll, 80); // scrolls every 80 milliseconds
}
function sleep(delay) {
	var start = new Date().getTime();
	while (new Date().getTime() < start + delay);
};
function calc(antchar,antcol) {
		var pheight = parseInt(document.body.offsetHeight);
		var hheight = parseInt(document.getElementById("Hode").offsetHeight);
		var thheight = parseInt(document.getElementById("tabhode").offsetHeight);
		var fheight = hheight;
		var res = (pheight - hheight - thheight - fheight - 10) + "px";
		var tab = (pheight - hheight - fheight - 10) + "px";
		var txw = document.getElementById("dv").offsetWidth;
		var tw = Math.round((txw*(antchar + (antcol * 2)))/10)*10;
		if(tw < document.body.offsetWidth)
{
			if (document.getElementById("Hode")) document.getElementById("Hode").setAttribute("style","width:" + tw);
			if (document.getElementById("tabhode")) document.getElementById("tabhode").setAttribute("style","width:" + tw);
			if (document.getElementById("scroll")) document.getElementById("scroll").setAttribute("style","width:" + tw);
		}
		else
{
			if (document.getElementById("tabhode")) document.getElementById("tabhode").setAttribute("style","width:100%");
			if (document.getElementById("scroll")) document.getElementById("scroll").setAttribute("style","width:100%");
		}
		if (document.getElementById("scroll")) document.getElementById("scroll").style.height = res;
		if (document.getElementById("scroll")) document.getElementById("tabell").style.height = tab;
		if (document.getElementById("scroll")) document.getElementById("scroll").style.display = "block";
		var trw = document.getElementsByTagName("TR")[0].offsetWidth;
		if(trw < document.body.offsetWidth)
		{
			if (document.getElementById("Hode")) document.getElementById("Hode").setAttribute("style","width:" + trw);
		}
}
