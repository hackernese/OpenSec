<div class="auth-wrap">
    <div class="card auth-card">
        <h1>Log in</h1>

        <form method="POST" action="/login">
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
                    autocomplete="current-password"
                    placeholder="••••••••"
                >
            </div>

            <button type="submit" class="btn btn-primary btn-block mt-2">
                Log in
            </button>
        </form>

        <p class="form-footer">
            No account yet? <a href="/register">Sign up</a>
        </p>
    </div>
</div>
