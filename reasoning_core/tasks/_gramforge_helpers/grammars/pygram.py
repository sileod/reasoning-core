import random
from gramforge import generate, init_grammar
try:
    from gramforge import Substitution, Constraint
except ImportError:
    Substitution = Constraint = None

# ---------------------------------------------------------------------------
# Design notes
# ---------------------------------------------------------------------------
# Types are modelled as three small strings: 'int', 'str', 'list'.
# A function's return type is recorded in state['funcs'][name] = (arity, ret_t,
# param_types). Typed call rules (CALL_INT / CALL_STR / CALL_LIST) filter the
# registry by return type and fall back to a same-typed atom when no function
# matches, so the rules are always safe to fire.
#
# Feature flags compose orthogonally: each feature (print, loops,
# conditionals, recursion, cross-calls) maps to rule registrations that are
# conditionally included. The grammar stays declarative.
#
# BODY_STMT and TOP_STMT are both flag-gated so loops/conditionals appear
# inside function bodies AND at top level.
# ---------------------------------------------------------------------------


def pygram_grammar(
    max_number=16,
    # --- feature flags --------------------
    mode='function',               # 'program' = full script; 'function' = just defs
    n_functions=2,
    main_signature=None,          # ((ptype, ...), ret_type) fixes f0 exactly;
                                  # None => f0 draws from param_types / return_types
    f0_is_root=None,              # None => True when mode='function', False otherwise.
                                  # When True, f_i can only call f_j for j >= i, so
                                  # f0 is the single root that can reach everyone.
    returns=True,
    type_hints=True,
    param_types=('int',),         # drawn uniformly per param
    return_types=None,            # defaults to param_types
    include_print=True,           # print statements (body AND top level)
    include_loops=True,           # for / while (body AND top level)
    include_conditionals=True,    # if / else (body AND top level)
    allow_recursion=True,
    allow_cross_calls=True,
    n_outer_inits=0,
):
    R = init_grammar(['py'])
    chars = list("abcdefghijklmnopqrstuvwxyz")
    param_types = tuple(param_types)
    return_types = tuple(return_types) if return_types is not None else param_types
    if mode not in ('program', 'function'):
        raise ValueError(f"mode must be 'program' or 'function', got {mode!r}")
    if f0_is_root is None:
        f0_is_root = (mode == 'function')
    # In function mode we need at least one function to actually emit something.
    if mode == 'function' and n_functions < 1:
        raise ValueError("mode='function' requires n_functions >= 1")

    # -------------------------------------------------------------------------
    # 1. Scope stack + registries
    # -------------------------------------------------------------------------
    state = {'scopes': [], 'loops': {}, 'funcs': {}, 'current_fn': None}

    # Valid types used throughout. Adding a new type is almost free: add it
    # here, provide a literal in _literal_of_type / _arg_of_type, and add
    # ADV_ASSIGN_TYPE / CALL / etc. rules as appropriate.
    TYPES = ('int', 'str', 'list')

    _TYPE_LITERALS = {
        'int':  lambda: str(random.randint(0, max_number)),
        'str':  lambda: random.choice(['"hi"', '"cat"', '"go"', '"sun"']),
        'list': lambda: "[0, 1, 2]",
    }

    def _new_scope(params=None, p_types=None):
        s = {'assigned': {}, 'last': set(), 'params': set(),
             'vars': {t: set() for t in TYPES}}
        for p, t in zip(params or (), p_types or ()):
            s['assigned'][p] = '0'
            s['vars'][t].add(p)
            s['params'].add(p)
        return s

    def cur(): return state['scopes'][-1]
    def push_scope(params=None, p_types=None):
        state['scopes'].append(_new_scope(params, p_types))
    def pop_scope(): state['scopes'].pop()

    def reset_state(ctx_node):
        state['scopes'] = [_new_scope()]
        state['loops']  = {}
        state['funcs']  = {}
        state['current_fn'] = None
        state['fn_plan'] = []
        state['fn_plan_idx'] = 0
        if n_functions > 0:
            _make_plan()
        return ""

    # -------------------------------------------------------------------------
    # 2. Context-sensitive helpers
    # -------------------------------------------------------------------------
    def concat(*args): return "".join(a.render('py') for a in args)

    def render_init(ctx_node):
        top = cur()
        pool = [c for c in chars if c not in top['assigned']]
        v = random.choice(pool or chars)
        d = str(random.randint(0, max_number))
        top['assigned'][v] = d
        top['vars']['int'].add(v)
        return f"{v} = {d}\n"

    def render_assign(v_node, e_node, kind='int'):
        v, e = v_node.render('py'), e_node.render('py')
        top = cur()
        top['last'] = {v}
        top['assigned'].setdefault(v, '0')
        for s in top['vars'].values(): s.discard(v)
        top['vars'][kind].add(v)
        return f"{v} = {e}\n"

    def get_var_of_type(t):
        """Walk the scope chain to find a variable of type `t`. Mirrors
        Python's lexical closure — inner bodies can reference outer-scope
        vars. If truly nothing is in scope, fabricate a new numeric var at
        the outermost scope (only meaningful for int; other types fall back
        to a literal via _arg_of_type)."""
        for scope in reversed(state['scopes']):
            pool = scope['vars'][t]
            if pool: return random.choice(list(pool))
        # Fabrication fallback (int only — for other types, caller should
        # use _arg_of_type which will emit a literal).
        outer = state['scopes'][0]
        v = random.choice(chars)
        outer['assigned'][v] = '0'
        outer['vars']['int'].add(v)
        return v

    # Alias used by int-context rules (EXPR_ID, DISP_EXPR, COND_EXPR, ...).
    def get_assigned_var(ctx): return get_var_of_type('int')

    def get_atom(ctx):
        if cur()['assigned'] and random.random() < 0.7:
            return get_assigned_var(ctx)
        return str(random.randint(0, max_number))

    def get_last_var(ctx):
        top = cur()
        return next(iter(top['last'])) if top['last'] else get_assigned_var(ctx)

    def render_loop_math(ctx_node, mode):
        if mode == 'init':
            val = str(random.randint(0, 20))
            state['loops']['val'] = val
            return val
        init_val = int(state['loops'].get('val', '0'))
        step, count = random.choice([(1, 2), (2, 1), (2, 2), (2, 3), (3, 2)])
        state['loops']['step'] = str(step)
        if mode == 'final_less':    return str(step * count + init_val - 1)
        if mode == 'final_greater': return str(init_val - step * count + 1)
        return "0"

    def render_while_var(ctx_node):
        v = get_assigned_var(ctx_node)
        state['loops']['var'] = v
        state['loops']['val'] = cur()['assigned'].get(v, '0')
        return v

    def render_while_update(ctx_node, op):
        v = state['loops'].get('var', 'i')
        s = state['loops'].get('step', '1')
        return f"{v} = {v} {op} {s}"

    def render_cond_expr(v1_node, op_node, v2_node):
        lhs, op, rhs = v1_node.render('py'), op_node.render('py'), v2_node.render('py')
        if lhs == rhs and random.random() < 0.8:
            alts = [c for c in cur()['vars']['int'] if c != lhs]
            if alts: rhs = random.choice(alts)
        return f"{lhs} {op} {rhs}"

    # -------------------------------------------------------------------------
    # 3. Typed calls
    # -------------------------------------------------------------------------
    def _fn_index(name):
        """Return the numeric index of a function name (e.g. 'f3' -> 3)."""
        return int(name[1:]) if name and name.startswith('f') else -1

    def _callable_functions(ret_type):
        candidates = []
        current = state['current_fn']
        current_idx = _fn_index(current)
        for fname, (arity, rt, ptypes) in state['funcs'].items():
            if rt != ret_type: continue
            is_self = (fname == current)
            if is_self and not allow_recursion: continue
            if (not is_self) and current is not None and not allow_cross_calls:
                continue
            # Hierarchy: when f0_is_root, f_i can only call f_j for j >= i.
            # This makes f0 the sole root that transitively reaches every
            # function, so "parsing f0" captures a self-contained call tree.
            if f0_is_root and current is not None:
                if _fn_index(fname) < current_idx:
                    continue
            candidates.append((fname, ptypes))
        return candidates

    def _render_call_of_type(ret_type):
        cands = _callable_functions(ret_type)
        if cands:
            fname, ptypes = random.choice(cands)
            args = [_arg_of_type(t) for t in ptypes]
            return f"{fname}({', '.join(args)})"
        return _TYPE_LITERALS[ret_type]()

    def _arg_of_type(t):
        """Pick a call-argument matching type `t`: a same-typed var from the
        scope chain when possible, else a typed literal."""
        for scope in reversed(state['scopes']):
            pool = scope['vars'][t]
            if pool and random.random() < 0.6:
                return random.choice(list(pool))
        return _TYPE_LITERALS[t]()

    render_call_int  = lambda ctx: _render_call_of_type('int')
    render_call_str  = lambda ctx: _render_call_of_type('str')
    render_call_list = lambda ctx: _render_call_of_type('list')

    # -------------------------------------------------------------------------
    # 4. Function defs
    # -------------------------------------------------------------------------
    def _pick_param_types(n): return [random.choice(list(param_types)) for _ in range(n)]

    def render_func_body(*stmt_nodes):
        parts = [s.render('py').rstrip('\n') for s in stmt_nodes]
        return '\n'.join(p for p in parts if p) + '\n'

    def _make_plan():
        """Build the f0..f(N-1) metadata plan and pre-populate state['funcs'].

        Pre-registering *before* any body renders has two effects:
        (1) cross-calls resolve in any direction (f0 can call f1 even though
            f1's body renders later, and vice versa).
        (2) f0 gets a fixed signature dictated by `main_signature` (or by the
            configured param_types/return_types when that's not set).
        """
        plan = []
        for i in range(n_functions):
            if i == 0 and main_signature is not None:
                ptypes_i, ret_t_i = main_signature
                ptypes_i = list(ptypes_i)
                n_params = len(ptypes_i)
            elif i == 0:
                # f0 draws from the configured type pools; arity still random.
                n_params = random.choice([1, 2])
                ptypes_i = _pick_param_types(n_params)
                ret_t_i = random.choice(list(return_types))
            else:
                # Subfunctions (f1..fN) draw fully at random.
                n_params = random.choice([1, 2])
                ptypes_i = _pick_param_types(n_params)
                ret_t_i = random.choice(list(return_types))
            fname = f"f{i}"
            state['funcs'][fname] = (n_params, ret_t_i, ptypes_i)
            plan.append((fname, n_params, ret_t_i, ptypes_i))
        state['fn_plan'] = plan
        state['fn_plan_idx'] = 0

    def render_func_def(body_node):
        """Render one function. Uses the pre-built plan so f0 matches the
        user's requested signature and all functions are already registered,
        enabling mutual calls regardless of textual order."""
        # Pull metadata from the pre-built plan (see _make_plan).
        idx = state['fn_plan_idx']
        state['fn_plan_idx'] = idx + 1
        fname, n_params, ret_t, ptypes = state['fn_plan'][idx]

        outer = cur()['assigned']
        pool = [c for c in chars if c not in outer]
        params = (random.sample(pool, n_params) if len(pool) >= n_params
                  else random.sample(chars, n_params))

        prev_current = state['current_fn']
        state['current_fn'] = fname
        push_scope(params=params, p_types=ptypes)
        body_text = body_node.render('py')

        top = cur()
        # Return-value selection. Normally picks a same-typed local (with a
        # preference for the most-recently touched one). With some
        # probability we return a call-expression instead — this boosts the
        # chance a recursion/cross-call actually exercises the call graph.
        type_pool = top['vars'][ret_t]
        if random.random() < 0.25:
            # Call-expression return: "return f0(...)" / "return f1(...)" / ...
            ret_v = _render_call_of_type(ret_t)
        elif top['last'] and (last_of_type := [v for v in top['last'] if v in type_pool]):
            ret_v = last_of_type[0]
        elif type_pool:
            ret_v = random.choice(list(type_pool))
        else:
            ret_v = {'int': '0', 'str': '""', 'list': '[]'}[ret_t]

        pop_scope()
        state['current_fn'] = prev_current

        if type_hints:
            sig = ', '.join(f"{p}: {t}" for p, t in zip(params, ptypes))
            header = f"def {fname}({sig}) -> {ret_t}:" if returns else f"def {fname}({sig}):"
        else:
            header = f"def {fname}({', '.join(params)}):"

        indented = _indent_block(body_text)
        tail = f"\n    return {ret_v}" if returns else ("" if indented else "\n    pass")
        return f"{header}\n{indented}{tail}\n"

    # -------------------------------------------------------------------------
    # 5. Grammar
    # -------------------------------------------------------------------------
    R('CTX', '')
    R('RESET(CTX)', reset_state)

    R('DIGIT',       lambda: str(random.randint(0, max_number)))
    R('SMALL_INDEX', lambda: str(random.randint(0, 1)))
    R('STR_LIT',     lambda: random.choice(['"hi"', '"cat"', '"go"', '"sun"']))
    R('LIST_LIT(DIGIT, DIGIT, DIGIT)', '[0, 1, 2]')
    R('VAR(CTX)',    lambda x: random.choice(chars))
    for op in ['+', '-', '*']:                    R('ARITH_OP', op)
    for op in ['<', '>', '<=', '>=', '!=', '==']: R('REL_OP',   op)
    R('LOG_PREFIX', 'not ')
    for op in ['and', 'or']: R('LOG_INFIX', op)

    R('EXPR_ID(CTX)', get_assigned_var)
    R('ATOM(CTX)',    get_atom)
    R('TERM(EXPR_ID)', '0'); R('TERM(DIGIT)', '0'); R('TERM(ATOM)', '0')
    R('EXPRESSION(TERM, ARITH_OP, TERM)', '0 1 2')
    R('EXPRESSION(TERM)', '0', weight=0.35)
    R('ENCLOSED(EXPRESSION)', '(0)')

    R('DISP_ID(CTX)', get_last_var)
    R('DISP_EXPR(EXPR_ID, ARITH_OP, EXPR_ID)', '0 1 2')
    R('DISP_EXPR(EXPR_ID, ARITH_OP, DIGIT)',   '0 1 2')
    R('LEN_EXPR(STR_LIT)',  'len(0)')
    R('LEN_EXPR(LIST_LIT)', 'len(0)')
    R('INDEX_EXPR(LIST_LIT, SMALL_INDEX)',     '0[1]')
    R('STR_INDEX_EXPR(STR_LIT, SMALL_INDEX)',  '0[1]')

    R('CALL_INT(CTX)',  render_call_int)
    R('CALL_STR(CTX)',  render_call_str)
    R('CALL_LIST(CTX)', render_call_list)
    R('TERM(CALL_INT)', '0', weight=0.6)

    # Boolean literals as ints: True/False are Python ints (True == 1,
    # False == 0), so they slot in anywhere an ATOM is accepted without
    # needing a separate type pool. Low weight — they're a minority flavor.
    R('BOOL_LIT', lambda: random.choice(['True', 'False']))
    R('ATOM(BOOL_LIT)', '0', weight=0.15)

    # Typed concat expressions — str+str and list+list. Arithmetic on ints
    # already exists via EXPRESSION; these complete the picture for the
    # other two types so assignments aren't restricted to literals/calls.
    R('STR_ATOM(STR_LIT)',       '0')
    R('STR_ATOM(CALL_STR)',      '0')
    R('STR_EXPR(STR_ATOM, STR_ATOM)',  '0 + 1')
    R('LIST_ATOM(LIST_LIT)',     '0')
    R('LIST_ATOM(CALL_LIST)',    '0')
    R('LIST_EXPR(LIST_ATOM, LIST_ATOM)', '0 + 1')

    # String methods producing strings (.upper, .lower, etc). Minimal set.
    R('STR_METHOD(STR_ATOM)', '0.upper()')
    R('STR_METHOD(STR_ATOM)', '0.lower()')

    R('INIT(CTX)', render_init)
    for n in [2, 3, 4, 5]:
        for k in range(1, n + 2):
            R(f"IDENT_INIT_{n}(" + ",".join(["INIT"]*k) + ")", concat)

    R('SIMPLE_ARITH(ENCLOSED)', '0')
    R('SIMPLE_ARITH(SIMPLE_ARITH, ARITH_OP, ENCLOSED)', concat, weight=0.5)
    R('SIMPLE_ASSIGN(VAR, EXPRESSION)', render_assign)
    R('SIMPLE_ASSIGNS', '')
    R('SIMPLE_ASSIGNS(SIMPLE_ASSIGN)', '0')

    R('ADV_ASSIGN_TYPE(VAR, SIMPLE_ARITH)', render_assign)
    R('ADV_ASSIGN_TYPE(VAR, EXPRESSION)',   render_assign)
    R('ADV_ASSIGN_TYPE(VAR, STR_LIT)',      lambda v, e: render_assign(v, e, kind='str'))
    R('ADV_ASSIGN_TYPE(VAR, LIST_LIT)',     lambda v, e: render_assign(v, e, kind='list'))
    R('ADV_ASSIGN_TYPE(VAR, LEN_EXPR)',     render_assign)
    R('ADV_ASSIGN_TYPE(VAR, INDEX_EXPR)',   render_assign)
    R('ADV_ASSIGN_TYPE(VAR, CALL_INT)',     render_assign, weight=3.0)
    R('ADV_ASSIGN_TYPE(VAR, CALL_STR)',     lambda v, e: render_assign(v, e, kind='str'), weight=2.0)
    R('ADV_ASSIGN_TYPE(VAR, CALL_LIST)',    lambda v, e: render_assign(v, e, kind='list'), weight=2.0)
    R('ADV_ASSIGN_TYPE(VAR, STR_EXPR)',     lambda v, e: render_assign(v, e, kind='str'),  weight=0.8)
    R('ADV_ASSIGN_TYPE(VAR, LIST_EXPR)',    lambda v, e: render_assign(v, e, kind='list'), weight=0.8)
    R('ADV_ASSIGN_TYPE(VAR, STR_METHOD)',   lambda v, e: render_assign(v, e, kind='str'),  weight=0.6)
    R('ADV_ASSIGNS', '')
    R('ADV_ASSIGNS(ADV_ASSIGN_TYPE)', '0')

    # Conditionals — rules defined; inclusion in BODY_STMT/TOP_STMT is gated.
    R('COND_EXPR(EXPR_ID, REL_OP, EXPR_ID)', render_cond_expr)
    R('COND_EXPR(EXPR_ID, REL_OP, DIGIT)',   '0 1 2')
    # Richer conditions: compare against len() or a function call.
    R('COND_EXPR(LEN_EXPR, REL_OP, DIGIT)',   '0 1 2', weight=0.4)
    R('COND_EXPR(EXPR_ID, REL_OP, CALL_INT)', '0 1 2', weight=0.4)
    R('COND(COND_EXPR)', '0')
    R('COND(LOG_PREFIX, COND_EXPR)', '01')
    R('ENCLOSED_COND(COND)', '(0)')
    R('CHAIN(ENCLOSED_COND)', '0')
    R('CHAIN(LOG_PREFIX, ENCLOSED_COND)', '01')
    R('CHAIN(CHAIN, LOG_INFIX, ENCLOSED_COND)', '0 1 2', weight=0.3)
    R('IF_BLK(COND)',    'if 0:\n')
    R('ELIF_BLK(COND)',  'elif 0:\n')
    R('ELSE_BLK',        'else:\n')
    R('ADV_IF(CHAIN)',   'if 0:\n')
    R('ADV_ELIF(CHAIN)', 'elif 0:\n')

    def _indent_block(text, prefix='    '):
        """Indent every non-empty line by `prefix`. Normalizes tabs to spaces
        so nested blocks end up uniformly indented."""
        out = []
        for line in text.split('\n'):
            if not line.strip(): continue
            out.append(prefix + line.replace('\t', '    '))
        return '\n'.join(out)

    # Compound if/else usable as a single statement.
    R('IF_STMT(IF_BLK, BODY_STMT)',
      lambda ib, s: f"{ib.render('py')}{_indent_block(s.render('py'))}\n")
    R('IF_STMT(IF_BLK, BODY_STMT, ELSE_BLK, BODY_STMT)',
      lambda ib, s1, el, s2:
          f"{ib.render('py')}{_indent_block(s1.render('py'))}\n"
          f"{el.render('py')}{_indent_block(s2.render('py'))}\n")

    # Display rules
    R('DISPLAY(DISP_ID)', 'print(0)')
    R('ADV_DISP(DISPLAY)',        '0')
    R('ADV_DISP(DISP_EXPR)',      'print(0)')
    R('ADV_DISP(STR_LIT)',        'print(0)')
    R('ADV_DISP(LIST_LIT)',       'print(0)')
    R('ADV_DISP(LEN_EXPR)',       'print(0)')
    R('ADV_DISP(INDEX_EXPR)',     'print(0)')
    R('ADV_DISP(STR_INDEX_EXPR)', 'print(0)')
    R('ADV_DISP(CALL_INT)',       'print(0)', weight=1.5)

    # Bare expression statement — alternative to print when include_print=False.
    R('EXPR_STMT(CALL_INT)',   '0\n')
    R('EXPR_STMT(CALL_STR)',   '0\n')
    R('EXPR_STMT(CALL_LIST)',  '0\n')
    R('EXPR_STMT(EXPRESSION)', '0\n')

    # Loops — unified rules (spaces-only indentation). Body is BODY_STMT so
    # loops inherit whatever flag-gating applies to statements.
    R('FOR_INIT(CTX)',  lambda x: render_loop_math(x, 'init'))
    R('FOR_FINAL(CTX)', lambda x: render_loop_math(x, 'final_less'))
    R('STEP(CTX)',      lambda x: state['loops'].get('step', '1'))
    R('FOR_HEAD(VAR, FOR_INIT, FOR_FINAL, STEP)', 'for 0 in range(1, 2, 3):')
    R('FOR_HEAD(VAR, FOR_INIT, FOR_FINAL)',       'for 0 in range(1, 2):')
    R('FOR_LOOP(FOR_HEAD, BODY_STMT)',
      lambda h, b: f"{h.render('py')}\n{_indent_block(b.render('py'))}\n")

    R('REL_LESS', '<');    R('REL_LESS', '<=')
    R('REL_GREATER', '>'); R('REL_GREATER', '>=')
    R('WHILE_VAR(CTX)',  render_while_var)
    R('WH_FINAL_L(CTX)', lambda x: render_loop_math(x, 'final_less'))
    R('WH_FINAL_G(CTX)', lambda x: render_loop_math(x, 'final_greater'))
    R('WH_UPD_L(CTX)',   lambda x: render_while_update(x, '+'))
    R('WH_UPD_G(CTX)',   lambda x: render_while_update(x, '-'))
    R('WH_L(WHILE_VAR, REL_LESS,    WH_FINAL_L, BODY_STMT, WH_UPD_L)',
      lambda v, op, f, b, u:
          f"while {v.render('py')} {op.render('py')} {f.render('py')}:\n"
          f"{_indent_block(b.render('py'))}\n    {u.render('py')}\n")
    R('WH_G(WHILE_VAR, REL_GREATER, WH_FINAL_G, BODY_STMT, WH_UPD_G)',
      lambda v, op, f, b, u:
          f"while {v.render('py')} {op.render('py')} {f.render('py')}:\n"
          f"{_indent_block(b.render('py'))}\n    {u.render('py')}\n")

    # -------------------------------------------------------------------------
    # 6. BODY_STMT — flag-gated
    # -------------------------------------------------------------------------
    R('BODY_STMT(SIMPLE_ASSIGN)',   '0')
    R('BODY_STMT(ADV_ASSIGN_TYPE)', '0')
    if include_print:
        R('BODY_STMT(DISPLAY)', '0')
    if include_loops:
        R('BODY_STMT(FOR_LOOP)', '0', weight=0.4)
        R('BODY_STMT(WH_L)',     '0', weight=0.3)
        R('BODY_STMT(WH_G)',     '0', weight=0.3)
    if include_conditionals:
        R('BODY_STMT(IF_STMT)',  '0', weight=0.5)

    # Functions
    R('FUNC_BODY(BODY_STMT)',                       render_func_body)
    R('FUNC_BODY(BODY_STMT, BODY_STMT)',            render_func_body)
    R('FUNC_BODY(BODY_STMT, BODY_STMT, BODY_STMT)', render_func_body)
    R('FUNC_DEF(FUNC_BODY)', render_func_def)

    # -------------------------------------------------------------------------
    # 7. TOP_STMT / FINAL_STMT — flag-gated
    # -------------------------------------------------------------------------
    # Every top-level rule that can emit output without a trailing newline
    # (e.g. ADV_DISP -> "print(0)") goes through an '\n'-terminating wrapper
    # to keep statement separation consistent.
    _stmt_end = lambda c: c.render('py').rstrip('\n') + '\n'
    R('TOP_ASSIGNS(ADV_ASSIGNS)', _stmt_end)
    R('TOP_DISP(ADV_DISP)',       _stmt_end)
    R('TOP_FOR(FOR_LOOP)',        _stmt_end)
    R('TOP_WH_L(WH_L)',           _stmt_end)
    R('TOP_WH_G(WH_G)',           _stmt_end)
    R('TOP_IF(IF_STMT)',          _stmt_end)
    R('TOP_EXPR(EXPR_STMT)',      _stmt_end)

    R('TOP_STMT(TOP_ASSIGNS)', '0')
    if include_print:
        R('TOP_STMT(TOP_DISP)',  '0', weight=1.2)
    if include_loops:
        R('TOP_STMT(TOP_FOR)',   '0', weight=0.5)
        R('TOP_STMT(TOP_WH_L)',  '0', weight=0.35)
        R('TOP_STMT(TOP_WH_G)',  '0', weight=0.35)
    if include_conditionals:
        R('TOP_STMT(TOP_IF)',    '0', weight=0.6)
    R('TOP_STMT(TOP_EXPR)',      '0')

    # MAIN_CALL: specifically exercise f0 with typed args, used as FINAL_STMT
    # when we're in flag mode with at least one function. This guarantees the
    # last line of every program actually invokes the designated main.
    def render_main_call(ctx):
        spec = state['funcs'].get('f0')
        if spec is None: return get_atom(ctx)
        _, _, ptypes = spec
        return f"f0({', '.join(_arg_of_type(t) for t in ptypes)})"
    R('MAIN_CALL(CTX)', render_main_call)

    if n_functions > 0:
        # Wrap the f0 call in print() when prints are allowed, bare otherwise.
        if include_print:
            R('FINAL_STMT(MAIN_CALL)', lambda c: f"print({c.render('py')})\n")
        else:
            R('FINAL_STMT(MAIN_CALL)', lambda c: f"{c.render('py')}\n")
    elif include_print:
        R('FINAL_STMT(TOP_DISP)', '0')
    else:
        R('FINAL_STMT(TOP_EXPR)', '0')

    # -------------------------------------------------------------------------
    # 8. Flag-based entry point
    # -------------------------------------------------------------------------
    # `function` mode: emit only `def f0(...) ... def fN(...)`. No outer inits,
    # no trailing top-level statement, no final call. The output is a raw
    # block of function definitions, suitable for parsing as-is.
    #
    # `program` mode (default): outer inits + functions + a free top-level
    # statement + a final call that exercises f0.
    if mode == 'function':
        prog_args = ['FUNC_DEF'] * max(1, n_functions)
    else:
        needs_numeric_fallback = n_functions > 0 and 'int' not in param_types
        effective_inits = max(n_outer_inits, 2 if needs_numeric_fallback else n_outer_inits)
        init_name = f'IDENT_INIT_{max(2, effective_inits)}' if effective_inits > 0 else None
        prog_args = []
        if init_name: prog_args.append(init_name)
        prog_args.extend(['FUNC_DEF'] * max(0, n_functions))
        prog_args.append('TOP_STMT')
        prog_args.append('FINAL_STMT')
    R(f"PROGRAM({','.join(prog_args)})", concat)

    # Root
    R('ALL(RESET, PROGRAM)', lambda r, p: r.render('py') + p.render('py'))
    R('start(ALL)', '0')
    return R
