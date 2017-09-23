import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ResponsiveSlideLoginDesigner } from './responsive-slides-login';


@NgModule({
  imports: [
    CommonModule
  ],
  declarations: [ ResponsiveSlideLoginDesigner ],
  exports: [ ResponsiveSlideLoginDesigner ]
})
export class ResponsiveSlidesModule { }
