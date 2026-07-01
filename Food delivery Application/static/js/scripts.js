document.addEventListener("DOMContentLoaded", function(){

    const search = document.getElementById("search");

    if(search){
        search.addEventListener("input", function(){
            const value = this.value.toLowerCase();
            const products = document.querySelectorAll(".product-card");

            products.forEach(product => {
                const text = product.innerText.toLowerCase();
                product.style.display = text.includes(value) ? "block" : "none";
            });
        });
    }

});