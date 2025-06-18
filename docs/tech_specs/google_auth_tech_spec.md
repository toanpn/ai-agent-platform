# Google Authentication Technical Specification

This document outlines the technical implementation details for adding Google Authentication to the platform, following the approach described in the [Code Maze article](https://code-maze.com/how-to-sign-in-with-google-angular-aspnet-webapi/).

## 1. Prerequisites

Before starting the implementation, we need to create OAuth 2.0 Client credentials on the [Google API Console](https://console.cloud.google.com/apis/credentials). This will provide a **Client ID** that will be used by both the frontend and backend applications.

- **Authorized JavaScript origins**: For development, this will be the URL of the Angular app (e.g., `http://localhost:4200`).
- **Authorized redirect URIs**: While not strictly required for this flow, it's good practice to configure it.

The Client ID should be stored securely and not be hardcoded directly in the source code.

## 2. Frontend (Angular) Implementation

The frontend will use the `@abacritt/angularx-social-login` library to handle the Google login flow.

### 2.1. Installation

```bash
npm install @abacritt/angularx-social-login
```

### 2.2. Module Configuration (`app.module.ts`)

We will configure the `SocialLoginModule` in our main application module.

```typescript
// ... existing code ...
import { SocialLoginModule, SocialAuthServiceConfig, GoogleLoginProvider } from '@abacritt/angularx-social-login';

// ... existing code ...

@NgModule({
  imports: [
    // ... other imports
    SocialLoginModule
  ],
  providers: [
    {
      provide: 'SocialAuthServiceConfig',
      useValue: {
        autoLogin: false, // Set to true to attempt auto-login on app load
        providers: [
          {
            id: GoogleLoginProvider.PROVIDER_ID,
            provider: new GoogleLoginProvider(
              'YOUR_GOOGLE_CLIENT_ID' // This should be loaded from environment config
            )
          }
        ],
        onError: (err) => {
          console.error(err);
        }
      } as SocialAuthServiceConfig,
    }
  ],
  // ... existing code ...
})
export class AppModule { }
```
**Note:** `YOUR_GOOGLE_CLIENT_ID` must be replaced with the actual client ID from the Google API Console and should be managed via environment variables (`environment.ts`).

### 2.3. Authentication Service (`auth.service.ts`)

The `auth.service.ts` will be extended to handle external authentication.

```typescript
// ... existing code ...
import { SocialAuthService, SocialUser } from "@abacritt/angularx-social-login";
import { GoogleLoginProvider } from "@abacritt/angularx-social-login";
import { Subject } from 'rxjs';

// ... existing code ...

export class AuthService {
  private extAuthChangeSub = new Subject<SocialUser>();
  public extAuthChanged = this.extAuthChangeSub.asObservable();

  constructor(
    private http: HttpClient,
    private externalAuthService: SocialAuthService
    // ... other dependencies
  ) {
    this.externalAuthService.authState.subscribe((user) => {
      this.extAuthChangeSub.next(user);
    });
  }

  public signInWithGoogle = () => {
    return this.externalAuthService.signIn(GoogleLoginProvider.PROVIDER_ID);
  }

  public signOutExternal = () => {
    return this.externalAuthService.signOut();
  }

  public logout = () => {
    // Clear the application's token
    localStorage.removeItem("token");
    // Sign out from the external provider
    this.signOutExternal();
    // Notify other parts of the app that auth state has changed
    // This assumes you have a similar mechanism for regular auth
    // this.authChangeSub.next(false); 
  }

  public externalLogin = (body: { provider: string, idToken: string }) => {
    // This will be the endpoint on our backend
    return this.http.post<AuthResponseDto>('api/auth/external-login', body);
  }

  // ... other methods
}
```

### 2.4. Login Component (`login.component.ts`)

The login component will have a button to trigger the Google sign-in and will handle the response.

```typescript
// ... existing code ...
import { AuthService } from '...'; // import your auth service
import { SocialUser } from '@abacritt/angularx-social-login';

export class LoginComponent implements OnInit {

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit(): void {
    this.authService.extAuthChanged.subscribe(user => {
      if (user) {
        this.validateExternalAuth(user);
      }
    });
  }

  signInWithGoogle(): void {
    this.authService.signInWithGoogle();
  }

  private validateExternalAuth(user: SocialUser) {
    const externalAuth = {
      provider: user.provider,
      idToken: user.idToken
    };

    this.authService.externalLogin(externalAuth).subscribe({
      next: (res) => {
        // Assuming the backend returns a JWT token
        localStorage.setItem("token", res.token);
        this.router.navigate(['/']);
      },
      error: (err) => {
        console.error(err);
        this.authService.signOutExternal();
      }
    });
  }
}
```

## 3. Backend (ASP.NET Core) Implementation

The backend will receive the `idToken` from the frontend, validate it, and then either create a new user or log in an existing user, returning a JWT for our application.

### 3.1. NuGet Packages

We will need the following package for Google token validation:
```
Google.Apis.Auth
```

### 3.2. Configuration (`appsettings.json`)

Add the Google Client ID to the configuration.

```json
{
  "Authentication": {
    "Google": {
      "ClientId": "YOUR_GOOGLE_CLIENT_ID"
    }
  }
}
```

### 3.3. API Controller (`AuthController.cs`)

Create a new endpoint to handle the external login.

```csharp
[ApiController]
[Route("api/auth")]
public class AuthController : ControllerBase
{
    // ... inject services for user management, token generation, and configuration

    [HttpPost("external-login")]
    public async Task<IActionResult> ExternalLogin([FromBody] ExternalAuthDto externalAuth)
    {
        var settings = new GoogleJsonWebSignature.ValidationSettings()
        {
            Audience = new List<string>() { _config["Authentication:Google:ClientId"] }
        };

        try
        {
            var payload = await GoogleJsonWebSignature.ValidateAsync(externalAuth.IdToken, settings);

            // Logic to find or create a user based on payload.Email
            var user = await _userManager.FindByEmailAsync(payload.Email);

            if (user == null)
            {
                // Create a new user if they don't exist
                user = new AppUser { UserName = payload.Email, Email = payload.Email, EmailConfirmed = true };
                var result = await _userManager.CreateAsync(user);
                if (!result.Succeeded)
                {
                    return BadRequest("User creation failed.");
                }
                // Add external login info
                await _userManager.AddLoginAsync(user, new UserLoginInfo(externalAuth.Provider, payload.Subject, externalAuth.Provider));
            }

            // Generate application-specific JWT
            var appToken = _tokenService.GenerateToken(user);

            return Ok(new AuthResponseDto { Token = appToken, IsAuthSuccessful = true });
        }
        catch (Exception ex)
        {
            // Invalid token
            return Unauthorized("Invalid external authentication.");
        }
    }
}
```

### 3.4. DTOs

Define the Data Transfer Objects for the request and response.

```csharp
// Request DTO
public class ExternalAuthDto
{
    [Required]
    public string Provider { get; set; }

    [Required]
    public string IdToken { get; set; }
}

// Response DTO
public class AuthResponseDto
{
    public bool IsAuthSuccessful { get; set; }
    public string Token { get; set; }
}
```

## 4. Integration with Existing Authentication

This section clarifies how the Google authentication flow integrates with a pre-existing email/password system managed by ASP.NET Core Identity.

### 4.1. Unified User Model & Token Generation

The key principle is that **the external login flow merges with the existing user management system**.

1.  **User Identity**: After the Google `idToken` is successfully validated, the backend uses the email from the token payload to find a user in the `AspNetUsers` table (`_userManager.FindByEmailAsync`).
    *   **Existing User**: If a user with that email already exists (e.g., they signed up previously with email/password), the system links their account to the Google provider by adding an entry to the `AspNetUserLogins` table.
    *   **New User**: If no user with that email exists, a new user is created in the `AspNetUsers` table, and the link to the Google provider is created in `AspNetUserLogins`. Their email is marked as confirmed by default since it's verified by Google.

2.  **Token Generation**: Once the backend has a reference to the user entity (either found or newly created), it calls the **exact same token generation service** that the regular email/password login uses (e.g., `_tokenService.GenerateToken(user)`).

This ensures that the JWT issued to the user is identical in structure, claims, and signature, regardless of whether they logged in with Google or a password. The rest of the application's authorized endpoints will continue to work seamlessly without any changes.

### 4.2. Logout Flow

The logout process is a client-side responsibility for a stateless JWT-based system.

1.  **Frontend**: The client calls the unified `logout()` method in the `AuthService`.
2.  This method performs two actions:
    *   It deletes the application's JWT from `localStorage`. This effectively logs the user out of our application.
    *   It calls `signOutExternal()` to clear the Google session from the browser. This is important to ensure the user isn't automatically logged back in via Google on their next visit and is presented with the choice to log in again.
3.  **Backend**: No backend call is necessary for logging out, as the JWT is stateless. The server will simply reject the deleted token if it's ever presented again.
