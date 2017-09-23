import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UnifyLoginDesigner } from './unify-login';
import { CarouseComponent } from './carousel.component'
import { CarouselModule } from 'ngx-bootstrap/carousel';
@NgModule({
    imports: [ CommonModule ,CarouselModule.forRoot()],
    declarations: [ 
        UnifyLoginDesigner,
        CarouseComponent
    ],
    exports: [
         UnifyLoginDesigner,
         CarouseComponent
         ]
})

export class UnifyTemplateModule {}