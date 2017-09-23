import { Inject, Injectable, forwardRef } from '@angular/core';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { User } from 'app/classes';
import { UserService } from 'app/services';
import { AuthService } from 'app/services/auth/auth.service'
import { tokenNotExpired, JwtHelper } from 'angular2-jwt';
import { Observable } from "rxjs";

@Injectable()
export class GlobalsService {
    private userSource = new BehaviorSubject<User>(null);
    user$ = this.userSource.asObservable();
    private userPermissionsSource = new BehaviorSubject<Array<string>>([]);
    userPermissions$ = this.userPermissionsSource.asObservable();
    private unreadNotifications = new BehaviorSubject<number>(0);
    unread_notifications$ = this.unreadNotifications.asObservable();

    constructor(
        @Inject(forwardRef(() => JwtHelper)) private jwtHelper,
        @Inject('Config') config

    ) {
        if (config.token) localStorage.setItem('id_token', config.token);
        this.setUser(config.user);
    }

    // Set or Change user value
    setUser(user: User) {
        if (user instanceof Object) {
            this.userPermissionsSource.next(user.permissions);
            delete user.permissions;
            this.userSource.next(user);
        }
        else {
            this.userSource.next(null);
            this.userPermissionsSource.next([]);
        }
    }

    // Set or Change unread notifications count
    setUnreadNfCount(count: number) { this.unreadNotifications.next(count); }

    private toastMessageSource = new BehaviorSubject<Array<string>>(['', 'success']);
    toastMessage = this.toastMessageSource.asObservable();
    setToastMessage(message: string, time: number, state?: string) {
        this.toastMessageSource.next([message, state || 'success']);
        time = time < 10000 && time != 0 ? 10000 : time;
        let timer = Observable.timer(time);

        timer.subscribe(() => {
            this.toastMessageSource.next(['', 'success']);
        });
    }

}
