import { Component,ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'app-root',
  encapsulation: ViewEncapsulation.None,
  templateUrl: './app.component.html',
  styleUrls: [
      './app.component.scss',
      './scss/theme/theme-1.css',
      './scss/application.scss'
  ],
host: {
      class:'theme-select'
  }
})
export class AppComponent {
  title = 'app works!';
}
