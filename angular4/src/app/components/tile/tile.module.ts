import { NgModule }      from '@angular/core';
import { LiveTile } from './tile.directive';

import 'metrojs/release/MetroJs.Full/MetroJs';
// import { SharedModule } from 'app/shared.module';

@NgModule({
  declarations: [
    LiveTile
  ],
  exports: [
    LiveTile
  ]
//   imports: [ SharedModule ]
})
export class LiveTileModule {
}
