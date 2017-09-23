import { Component ,Input,Output, EventEmitter} from '@angular/core';
import { CarouselConfig } from 'ngx-bootstrap/carousel';
@Component({
 selector: 'carousel-app',
 templateUrl: './carousel.html',
 providers: [{provide: CarouselConfig, useValue: {interval: 4000, noPause: true}}]
})
export class CarouseComponent {
    public images:Array<Object> = [];
    @Input('imageList') data;
    @Output() product_info_event = new EventEmitter();
    ngAfterContentInit(): void {
        this.images.push({
            "title":'default',
            "url":"assets/img/marketplace-banner.jpg",
            'id':null
        })
        if (this.data) {
            this.data.forEach(element => {
                //imag_source.push(element.banner_upload)
                this.images.push({
                    'title':element.description,
                    'url':element.banner_upload,
                    'id':element.id
                })
            });
        } 
    }    
    navigate_isv_product(data: any): any{
        this.product_info_event.emit({
            data: data
        });
    }
}