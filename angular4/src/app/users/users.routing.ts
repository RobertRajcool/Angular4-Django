import { RouterModule, Routes } from '@angular/router';

import { UsersComponent } from './users.component';
import { AddUserComponent } from './adduser.component';
import { EditUserComponent } from './edituser.component';
import { UsersListComponent } from './userslist/userslist.component'
import { RolesComponent } from './roles/roles.component'
import {UsersViewComponent} from "./users-view/users-view.component";

const UserRoutes : Routes = [
    { path: '', redirectTo: 'list', pathMatch: 'full'},
    {
        path: '',
        component: UsersComponent,
        children: [
            {
                path: 'roles',
                component: RolesComponent
            },
            {
                path:'list',
                component : UsersListComponent
            },
            {
                path: 'addUser',
                component: AddUserComponent
            },
            {
                path: ':id',
                component: EditUserComponent
            },
            {
                path: 'view/:id',
                component:UsersViewComponent
            }
        ]
    }

];

export const UserRouting = RouterModule.forChild(UserRoutes);
