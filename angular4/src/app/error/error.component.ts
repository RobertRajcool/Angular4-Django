import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'error',
  styleUrls: ['./error.style.scss'],
  templateUrl: './error.template.html',
  encapsulation: ViewEncapsulation.None,
  host: {
    class: 'error-page app'
  },

})
export class ErrorComponent { }
