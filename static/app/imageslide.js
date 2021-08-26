function show(){
    var x = document.getElementById("showw");
    if (x.style.display === "none")
    {
    x.style.display = "block";
    //x.style.class="w3-dropdown-hover"
    // document.getElementById("Close").innerHTML = "Close";
    x.style.width = "100%";
    }
    else{
    x.style.display = "none";
    }
}
function expand(number){
    var y = event.target.firstElementChild;
    if(y.style.display==="none")
    {
    y.style.display = "block";

    }
    else{
    y.style.display = "none";
    }
}

var images=["computerclubimage.jpg","Computing-feat.jpg", "computingimage.jpg","shutterstock.jpg"]
automatic();
var count =0;
function automatic(){
    var heightt = screen.height - 200; 
    
    if(count < images.length-1 || count < 0){
        ++count;
        document.getElementById('slide').src = "static/app/"+images[count];
        document.getElementById("slide").height = heightt;
        
    }
    else if(typeof count == "undefined")
    {
        document.getElementById('slide').src = "static/app/"+images[0];
        document.getElementById("slide").height = heightt;
        
    }
    else if (count + 2 >= images.length){
        count=0;
        document.getElementById('slide').src = "static/app/"+images[0];
        document.getElementById("slide").height = heightt;


    }
    else{
        ++count;
    }
    
}
setInterval(automatic, 6000);