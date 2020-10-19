document.addEventListener('DOMContentLoaded', function(){

    var totalsec = 0
    var seconds = 0;
    var minutes = 0;

    function timer(){
        totalsec++
        seconds++
        if(seconds==60){
            minutes++
            seconds=0;
        }
        document.querySelector('#time').innerHTML = `Elapsed time ${("0" + minutes).slice(-2)}:${("0" + seconds).slice(-2)}`;
    }

    var time = setInterval(timer, 1000)
    var timebttn = true;

    document.querySelector('#displaytimer').onclick = function(){
        if(timebttn==true){
            timebttn = false;
            document.querySelector('#time').style.display = 'none';
            document.querySelector('#displaytimer').innerHTML = 'Show Timer';
        }else{
            timebttn = true;
            document.querySelector('#time').style.display = 'block';
        }
    }

    dropboxes = document.querySelectorAll('.dropbox');

    cards = document.querySelectorAll('.card');
    n = cards.length;

    var cheights = [];
    var cwidths = [];

    for(var i=0; i<n; i++){
        cheights.push(parseInt(cards[i].clientHeight));
        cwidths.push(parseInt(cards[i].clientWidth));
    }

    const cheight = Math.max.apply(Math, cheights);
    const cwidth = Math.max.apply(Math, cwidths);

    for(var i=0; i<n; i++){
        cards[i].style.height = cheight + 'px';
        cards[i].style.width = cwidth + 'px';
        dropboxes[i].style.height = cheight + 20 +'px';
        dropboxes[i].style.width = cwidth + 20 +'px';
    }

    var fill = [];
    var correct = [];

    //Loop over all elements to space them out.
    for(var i=0; i<n; i++){
        dropboxes[i].style.left = (cwidth+23)*(i%5) + 20+ 'px';
        dropboxes[i].style.top = (cheight+23)*Math.floor(i/5) + 70 + 'px';
        cards[i].style.left = (cwidth+20)*(i%5) + 20 + 'px';
        fill.push(99);
        correct.push(i);
    }

    lastbox = dropboxes[n-1].getBoundingClientRect();

    for(var i=0; i<n; i++){
        cards[i].style.top = lastbox.bottom + (cheight+20)*Math.floor(i/5) + 20 + 'px';
    }

    
    
    cards.forEach(
        function(card){
            var selected = false;

            card.onmousedown = function(event){
                selected = true;
                let bin = null;
                let currbox = null;
                let cardi = parseInt(card.dataset.cindex);

                card.style.background='#d8205f';
                document.body.append(card);

                let shiftX = event.clientX - card.getBoundingClientRect().left;
                let shiftY = event.clientY - card.getBoundingClientRect().top;

                if(fill.includes(cardi)){
                    let ind = fill.indexOf(cardi);
                    fill[ind] = 99;
                    document.querySelector(`[data-bindex="${ind}"]`).style.background = "";
                }

                function moveCard(pageX, pageY){
                    card.style.left = pageX - shiftX + 'px';
                    card.style.top = pageY - shiftY + 'px';

                    var cleft = parseInt(card.style.left);
                    var cright = parseInt(card.style.left+'200px');
                    var ctop = parseInt(card.style.top);
                    var cbottom = parseInt(card.style.top+'100px');

                    dropboxes.forEach(function(box){

                        var boxxy = box.getBoundingClientRect();
                    
                        if(boxxy.left < cleft && boxxy.right > cright && boxxy.top < ctop && boxxy.bottom > cbottom){
                            if(selected===true){
                                if(box.style.background!="cadetblue"){
                                    box.style.background = "grey";
                                    currbox = box;
                                    bin = currbox;
                                }
                            }
                        }else{
                            if(box.style.background!="cadetblue"){
                                box.style.background = "";
                            }
                        }
                        
                    })
                }

                let currentbin = null;
            
                function onMouseMove(event){
                    moveCard(event.pageX, event.pageY);                    
                }

                moveCard(event.pageX, event.pageY);

                document.addEventListener('mousemove', onMouseMove);

                card.onmouseup = function(){
                    document.removeEventListener('mousemove', onMouseMove);
                    card.style.background = 'lightsalmon';
                    selected = false;
                    card.onmouseup = null;
                    if(currbox!=null && currbox.style.background==="grey"){
                        if(bin==currbox){
                            currbox.style.background = "cadetblue";
                            fill[currbox.dataset.bindex] = cardi;
                            // document.querySelector('.order').innerHTML = fill;
                            if(JSON.stringify(fill)===JSON.stringify(correct)){
                                document.querySelector('.check').innerHTML = "Success!";
                                document.querySelector('#info').style.color = "#d8205f";
                                clearInterval(time)
                                console.log(totalsec);
                                if(document.querySelector('#nextbutton').style.display=='none'){
                                    document.querySelector('#nextbutton').style.display='block';

                                    document.querySelector('#submittimebutton').innerHTML = `<button name="time" value=${totalsec}>Submit Time</button>`
                                }
                                // alert("Congratulations, you've won!");
                            }
                        }
                    }
                    // else{
                    //     document.querySelector('.order').innerHTML = fill;
                    // }
  
                }
            }

            card.ondragstart = function(){
                return false;
            }

            
        }
    )
});