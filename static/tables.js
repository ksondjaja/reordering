document.addEventListener('DOMContentLoaded', function(){
    const dividers = document.querySelectorAll('.divider');
    const tablediv = document.querySelectorAll('#tablediv');
    div1 = true;
    div2 = false;

    dividers[0].style.background = '#DED7FA';
    tablediv[0].style.display = 'table';
    tablediv[1].style.display = 'none';

    dividers[0].onclick = function(){
        dividers[0].style.background = '#DED7FA';
        dividers[1].style.background = '#F1EEFD';
        tablediv[0].style.display = 'table';
        tablediv[1].style.display = 'none';
        div1 = true;
        div2 = false;
    }

    dividers[1].onclick = function(){
        dividers[0].style.background = '#F1EEFD';
        dividers[1].style.background = '#DED7FA';
        tablediv[0].style.display = 'none';
        tablediv[1].style.display = 'table';
        div1 = false;
        div2 = true;
    }

    dividers.forEach(function(divider){
        divider.onmouseover = function(){
            divider.style.background =  '#DED7FA';
        }
        divider.onmouseout = function(){
            if(div1==false){
                dividers[0].style.background = '#F1EEFD';
            }else if(div2==false){
                dividers[1].style.background = '#F1EEFD';
            }
        }
    })
})