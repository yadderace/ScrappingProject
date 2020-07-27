CREATE TABLE public.encabezadoregistros
	(
    codigoencabezado bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    idregistro bigint NOT NULL,
    linkpagina character varying(500) COLLATE pg_catalog."default" NOT NULL,
    fecharegistro date NOT NULL DEFAULT now(),
    registrolimpio bool NOT NULL DEFAULT false,
    fechalimpieza timestamp without time zone,
    CONSTRAINT encabezadoregistros_pkey PRIMARY KEY (codigoencabezado)
)
    

CREATE TABLE public.detalleregistros
(
    codigodetalle bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    codigoencabezado bigint NOT NULL,
    nombrecampo character varying(100) COLLATE pg_catalog."default" NOT NULL,
    valorcampo character varying(100) COLLATE pg_catalog."default",
    valorjson json,
    fecharegistro date NOT NULL DEFAULT now(),
	CONSTRAINT detalleregistros_codigoencabezado_fkey FOREIGN KEY (codigoencabezado)
        REFERENCES public.encabezadoregistros (codigoencabezado) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)


CREATE TABLE public.limpiezalog
(
    idlimpiezalog bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    cantidadregistros bigint NOT NULL,
    fechalimpieza timestamp without time zone DEFAULT now(),
    CONSTRAINT limpiezalog_pkey PRIMARY KEY (idlimpiezalog)
);


CREATE TABLE public.limpiezadetalle
(
    idlimpiezadetalle bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    idlimpiezalog bigint NOT NULL,
    nombrecampo character varying(50) NOT NULL,
	tipodatacampo character varying(50) NOT NULL,
	fecharegistro timestamp without time zone DEFAULT now(),
	CONSTRAINT limpiezadetalle_pkey PRIMARY KEY (idlimpiezalog, nombrecampo),
	CONSTRAINT limpiezadetalle_idlimpiezalog_fkey FOREIGN KEY (idlimpiezalog)
        REFERENCES public.limpiezalog(idlimpiezalog) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);


CREATE TABLE public.limpiezadata
(
    idlimpiezadata bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
	nombrecampo character varying (50) NOT NULL,
	idlimpiezalog bigint NOT NULL,
    codigoencabezado bigint NOT NULL,
    valordata text,
	fecharegistro timestamp without time zone DEFAULT now(),
	CONSTRAINT limpiezadata_pkey PRIMARY KEY (idlimpiezadata),
	CONSTRAINT limpiezadata_idlimpiezadetalle_fkey FOREIGN KEY (idlimpiezalog, nombrecampo)
        REFERENCES public.limpiezadetalle (idlimpiezalog, nombrecampo) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT limpiezadetalle_codigoencabezado_fkey FOREIGN KEY (codigoencabezado)
        REFERENCES public.encabezadoregistros(codigoencabezado) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);


CREATE TABLE public.modeloencabezado
(
    idmodelo bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    tipomodelo character varying(5) NOT NULL,
    archivomodelo character varying(50) NOT NULL,
	msescore float NOT NULL DEFAULT 0,
	r2score float NOT NULL DEFAULT 0,
	active boolean NOT NULL DEFAULT false,
	fecharegistro timestamp without time zone DEFAULT now(),
	CONSTRAINT construccionmodelo_pkey PRIMARY KEY (idmodelo)
);


CREATE TABLE public.modelocampo
(
    idmodelocampo bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    idmodelo bigint NOT NULL,
    nombrecampo character varying(50) NOT NULL,
	tipodatacampo character varying NOT NULL DEFAULT 0,
	fecharegistro timestamp without time zone DEFAULT now(),
	CONSTRAINT modelocampo_pkey PRIMARY KEY (idmodelo, nombrecampo),
	CONSTRAINT modelocampo_idmodelo_fkey FOREIGN KEY (idmodelo)
        REFERENCES public.modeloencabezado(idmodelo) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);


CREATE TABLE public.modelodata
(
    idmodelodata bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
	idmodelo bigint NOT NULL,
    nombrecampo character varying (50) NOT NULL,
	codigoencabezado bigint NOT NULL,
    valordata text,
	tipodata char(2) NOT NULL,
	fecharegistro timestamp without time zone DEFAULT now(),
	CONSTRAINT modelodata_pkey PRIMARY KEY (idmodelodata),
	CONSTRAINT modelodata_idmodelo_fkey FOREIGN KEY (idmodelo, nombrecampo)
        REFERENCES public.modelocampo (idmodelo, nombrecampo) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT modelodata_codigoencabezado_fkey FOREIGN KEY (codigoencabezado)
        REFERENCES public.encabezadoregistros(codigoencabezado) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);


CREATE TABLE public.logaccionessistema
(
    idlogacciones bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    nombreaccion character varying (50) NOT NULL,
    descripcionaccion text,
    fechaaccion timestamp without time zone DEFAULT now() 
)