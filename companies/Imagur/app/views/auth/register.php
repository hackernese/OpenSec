<div class="auth-wrap">
    <div class="card auth-card">
        <h1>Create account</h1>

        <form method="POST" action="/register">
            <div class="form-group">
                <label for="email">Email address</label>
                <input
                    type="email"
                    id="email"
                    name="email"
                    required
                    autofocus
                    autocomplete="email"
                    placeholder="you@example.com"
                >
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input
                    type="password"
                    id="password"
                    name="password"
                    required
                    autocomplete="new-password"
                    placeholder="Min. 8 characters"
                    minlength="8"
                >
            </div>

            <div class="form-group">
                <label for="confirm">Confirm password</label>
                <input
                    type="password"
                    id="confirm"
                    name="confirm"
                    required
                    autocomplete="new-password"
                    placeholder="••••••••"
                >
            </div>

            <button type="submit" class="btn btn-primary btn-block mt-2">
                Create account
            </button>
        </form>

        <p class="form-footer">
            Already have an account? <a href="/login">Log in</a>
        </p>
    </div>
</div>
