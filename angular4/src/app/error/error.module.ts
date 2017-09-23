import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';

import { ErrorComponent } from './error.component';
import { PermissionDeniedComponent } from './permission-denied/permission-denied.component';
import { NotFoundComponent } from './not-found/not-found.component';
import { DetailNotFoundComponent } from './detail-not-found/detail-not-found.component';

export const routes = [
  { path: '', redirectTo: '', pathMatch: 'full' },
  {
    path: '',
    component: ErrorComponent,
    children: [
      { path: 'not-found', component: NotFoundComponent },
      { path: 'denied', component: PermissionDeniedComponent },
      { path: 'detail-not-found', component: DetailNotFoundComponent }
    ]
  },
];

@NgModule({
  declarations: [
    ErrorComponent,
    PermissionDeniedComponent,
    NotFoundComponent,
    DetailNotFoundComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    RouterModule.forChild(routes),
  ]
})
export class ErrorModule {
  static routes = routes;
}
