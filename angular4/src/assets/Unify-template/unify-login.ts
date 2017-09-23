import { Directive, ElementRef, ViewEncapsulation, OnDestroy } from '@angular/core';
declare var jQuery: any;

@Directive({
    selector: '[UnifyLoginDesigner]',
    host: {
        '(window:load)': 'handleEqualHeightColumns($event)',
        '(window:resize)': 'handleEqualHeightColumns($event)'
    }
})

export class UnifyLoginDesigner {
    BannerLoopTimer: any;
    $el: any;

    constructor(el: ElementRef) {
        this.$el = jQuery(el.nativeElement);
    }

    ngAfterContentInit(): void {
        this.handleEqualHeightColumns('36rem');
        this.imageSlider([
            "assets/img/pictures/banner100.png",
            "assets/img/pictures/banner20.jpg",
            "assets/img/pictures/banner9.jpg",
            "assets/img/pictures/banner3.jpg",
            "assets/img/pictures/banner18.jpg",
            "assets/img/pictures/banner10.jpg",
            "assets/img/pictures/banner14.jpg",
            "assets/img/pictures/banner1.jpg",
            "assets/img/pictures/banner15.jpg",
            "assets/img/pictures/banner16.jpg",
            "assets/img/pictures/banner17.png",
            "assets/img/pictures/banner8.jpg",
        ], 1000, 5000);
    }

    // Equal Height Columns
    handleEqualHeightColumns(height: string, event?: any) {
        var EqualHeightColumns = function () {
            jQuery(".equal-height-columns").each(function () {
                var heights = [];
                jQuery(".equal-height-column", this).each(function () {
                    jQuery(this).removeAttr("style");
                    heights.push(height); // write column's heights to the array
                });
                jQuery(".equal-height-column", this).height(Math.max.apply(Math, heights)); //find and set max
            });
        }

        EqualHeightColumns();
    }

    // Image slider animation
    imageSlider(imgLinks: Array<string>, fade: number, duration: number) {
        jQuery(this.$el).find(".image-block").each((index, imgBlock: HTMLDivElement) => {
            var linkIndex = 0;

            var createImgElement = (imgLink) => {
                let imgElement: HTMLImageElement = document.createElement('img');
                imgElement.setAttribute('src', imgLink);
                imgElement.style.position = 'absolute';
                imgElement.style.margin = '0';
                imgElement.style.padding = '0';
                imgElement.style.border = 'none';
                imgElement.style.zIndex = '-999999';
                imgElement.style.width = 'auto';
                imgElement.style.height = '100%';
                imgElement.style.transition = `opacity ${fade * 4 / 1000}s ease`;
                imgElement.style.opacity = '0';

                return imgElement;
            };

            var prevImg: HTMLImageElement = createImgElement(imgLinks[linkIndex]);
            imgBlock.appendChild(prevImg);
            prevImg.style.opacity = '1';

            // Looping Images
            var imgLooper = () => {
                this.BannerLoopTimer = setTimeout(() => {
                    if (linkIndex < imgLinks.length - 1) linkIndex += 1;
                    else linkIndex = 0;
                    // Changing src
                    var nextImg: HTMLImageElement = createImgElement(imgLinks[linkIndex]);

                    prevImg.style.opacity = '0';
                    imgBlock.appendChild(nextImg);
                    setTimeout(() => { nextImg.style.opacity = '1'; }, fade / 2);
                    // Removing previous image
                    setTimeout(() => { imgBlock.removeChild(prevImg); prevImg = nextImg; }, fade * 4);
                    imgLooper();
                }, duration);
            }; imgLooper();

        });
    }

    ngOnDestroy() {
        if (this.BannerLoopTimer) {
            clearTimeout(this.BannerLoopTimer);
        }
    }

}
