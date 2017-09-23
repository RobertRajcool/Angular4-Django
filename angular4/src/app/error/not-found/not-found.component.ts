import { Component, ViewEncapsulation, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-not-found',
  templateUrl: './not-found.component.html',
  encapsulation: ViewEncapsulation.None,
})
export class NotFoundComponent implements OnInit {

  router: Router;

  constructor(router: Router) {
    this.router = router;
  }

  searchResult(): void {
    // this.router.navigate(['/app', 'extra', 'search']);
  }

  ngOnInit() { }

}
