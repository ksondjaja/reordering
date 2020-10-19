document.addEventListener('DOMContentLoaded', function(){
    var accordions = document.querySelectorAll('.accordion');
    var previous;

    for (var i = 0; i < accordions.length; i++) {
        accordions[i].onclick = function() {
            if(previous){
                previous.classList.toggle("active",false);
                previous.nextElementSibling.classList.toggle("show",false);
                previous.nextElementSibling.style.display = "none";
                previous.style.background = "#afd7d8";
            }
            this.classList.toggle("active");
            this.nextElementSibling.classList.toggle("show");
            this.nextElementSibling.style.display = "block";
            this.style.background = "cadetblue";
            previous=this;
        }
    }

    document.querySelector('#nfields').onclick = function(){
        var numfields = document.querySelector('#segmentnumber').value;
    
        document.querySelector('#inputform').style.display = "block";
    
        var x = "";
        var i;
        for(i=0; i<numfields; i++){
            x = x + `Card number ${i+1}: <input name='${i}' type="text" placeholder="Enter text" required><br>`;
        }
        document.querySelector('#inputfields').innerHTML = x;
    }

    var gameinput = '{{  gameinput|safe  }}';
    
    if(gameinput.length >0){
        var gamevalues = {{  segmentvalues|safe  }};
        // var gamevalues = JSON.parse(segmentvalues);
        var n = Object.keys(gamevalues).length;

        document.querySelector('#segmentnumber').value = `${n}`;

        if(gameinput=='multifields'){

            accordions[1].onclick = function(){
                document.querySelector('#inputform').style.display = "block";
    
                var x = "";    
                for(var i=0; i<n; i++){
                    x = x + `Card number ${i+1}: <input name='${i}' type="text" value={{  segmentvalues.'${i}'|safe  }} placeholder="Enter text" required><br>`;
                }
                document.querySelector('#inputfields').innerHTML = x;
            }
        }
        if(gameinput=='paragraph'){
            accordions[0].onclick = function(){
                var x="";
                for(var i=0; i<n; i++){
                    x = x + `{{  segmentvalues.'${i}'|safe  }}`;
                }
                document.querySelector('#inputparagraph').innerHTML = x;
            }
        }
    }

    


})