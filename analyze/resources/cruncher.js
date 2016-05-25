"use strict"
/*
Large result cruncher
Hides results that are too large from the result table

Casey Primozic
*/
var hiddenText = []

$(document).ready(()=>{
  $(".long").each((index, elem)=>{
    hiddenText.push(elem.innerText);
    elem.removeAttribute("class");
    elem.setAttribute("id", `minimized-${hiddenText.length-1}`);
    elem.setAttribute("class", "minimized");
    elem.innerText = "Click to view";
  });

  $(".minimized").click(function(){
    var elem = $(this)[0];
    var index = elem.getAttribute("id").split("-")[1];
    $("#maximize").html(hiddenText[index]);
  });
});
